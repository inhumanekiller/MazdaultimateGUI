# mazda_tool/core/executor.py
import time
import threading
import logging
from typing import Callable, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("MazdaExecutor")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(ch)

class ExecutorStopException(Exception):
    pass

class ECUExecutor:
    """
    ECU Executor
    - Consumes queued actions produced by managers (TorqueManager, SecurityManager, etc.)
    - Supports 'simulation' mode and a hardware placeholder mode
    - Handles expires_at for temporary actions
    - Calls back to the originating manager via provided mark_action_done hook
    """

    def __init__(self,
                 queue_provider: Callable[[], list],
                 mark_done: Callable[[int, bool, str], bool],
                 mode: str = "simulation",
                 loop_period: float = 1.0):
        """
        Args:
            queue_provider: function returning a list of queued actions (in same order shown to UI).
                            Each item should be a dict with keys: queued_at, status, action
            mark_done: callback to notify manager when action completed: mark_done(index, success, message)
            mode: 'simulation' or 'hardware' (hardware is placeholder; not implemented here)
            loop_period: seconds between queue scans
        """
        assert mode in ("simulation", "hardware"), "mode must be 'simulation' or 'hardware'"
        self.queue_provider = queue_provider
        self.mark_done = mark_done
        self.mode = mode
        self.loop_period = loop_period
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                logger.info("Executor already running")
                return
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._main_loop, daemon=True)
            self._thread.start()
            logger.info("ECUExecutor started in %s mode", self.mode)

    def stop(self):
        with self._lock:
            self._stop_event.set()
            if self._thread:
                self._thread.join(timeout=5.0)
            logger.info("ECUExecutor stopped")

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _main_loop(self):
        try:
            while not self._stop_event.is_set():
                try:
                    self._process_queue_once()
                except ExecutorStopException:
                    break
                except Exception as e:
                    logger.exception("Executor loop exception: %s", e)
                time.sleep(self.loop_period)
        finally:
            logger.info("Executor loop exiting")

    def _process_queue_once(self):
        queue = self.queue_provider() or []
        now_ts = time.time()

        # 1) Clean expired temporary actions (mark as done/failed appropriately)
        for idx, rec in enumerate(queue):
            action = rec.get("action", {})
            expires_at = action.get("expires_at")
            if expires_at and expires_at <= now_ts and rec.get("status") == "queued":
                logger.info("Auto-expiring action idx=%d type=%s", idx, action.get("type"))
                # Mark expired as done=false with message "expired"
                self.mark_done(idx, False, "expired/auto-removed")
                # continue to next (note: managers should remove or mark done; we call mark_done)

        # refresh queue after possible expirations
        queue = self.queue_provider() or []

        # 2) Process first queued action (FIFO)
        for idx, rec in enumerate(queue):
            if rec.get("status") != "queued":
                continue
            action = rec.get("action", {})
            typ = action.get("type", "<unknown>")
            logger.info("Processing queued action idx=%d type=%s", idx, typ)

            # 3) Simulation mode behavior
            if self.mode == "simulation":
                # Simulate a hardware write latency proportional to complexity
                simulated_latency = self._simulate_latency_for_action(action)
                logger.info("Simulating action (sleep %.2fs): %s", simulated_latency, action)
                time.sleep(simulated_latency)

                # Basic validation: if action contains invalid fields, fail
                success, message = self._simulate_action_result(action)
                logger.info("Simulated result idx=%d success=%s msg=%s", idx, success, message)
                self.mark_done(idx, success, message)
                # Process only one action per scan to keep UI responsive
                return

            # 4) Hardware mode placeholder - DO NOT implement bypasses here
            if self.mode == "hardware":
                # This is where a J2534/Tactrix executor would be invoked.
                # For safety & legal reasons we *do not* implement OEM-security bypass here.
                # Instead we provide the correct integration points for your hardware library.
                logger.info("Hardware mode - placeholder for real ECU writes (action=%s)", action)
                # For now, mark as failed with a message explaining missing hardware integration.
                self.mark_done(idx, False, "hardware-mode not implemented: connect J2534 executor")
                return

        # nothing queued -> idle
        return

    def _simulate_latency_for_action(self, action: Dict[str, Any]) -> float:
        # Rough heuristic: simpler actions = quicker, complex flash = longer
        typ = action.get("type", "")
        if typ.startswith("temp_"):
            return 0.6
        if typ in ("apply_valet", "remove_valet", "immobilizer"):
            return 1.2
        if typ in ("gear_torque_limit", "temp_gear_clamp", "temp_timing_reduction"):
            return 0.8
        return 0.5

    def _simulate_action_result(self, action: Dict[str, Any]) -> (bool, str):
        """
        Simulate whether an action would succeed.
        Basic checks:
          - If action asks for weird values, fail.
          - Otherwise succeed.
        """
        typ = action.get("type", "")
        # Example validation rules
        if typ == "temp_timing_reduction":
            deg = float(action.get("deg", 0))
            if not (0 < deg <= 10):
                return False, "invalid_timing_deg"
            return True, f"applied_timing_reduction_{deg}deg"

        if typ == "temp_gear_clamp":
            val = float(action.get("value", 0))
            if val < 50:
                return False, "clamp_too_low"
            return True, f"applied_temp_gear_clamp_{val}"

        if typ == "gear_torque_limit":
            val = float(action.get("value", 0))
            if val < 50 or val > 1000:
                return False, "invalid_torque_value"
            return True, "queued_gear_limit_applied"

        if typ in ("apply_valet", "remove_valet"):
            return True, "valet_action_simulated"

        if typ == "immobilizer":
            # simulation: accept both lock/unlock
            return True, f"immobilizer_{'locked' if action.get('lock') else 'unlocked'}"

        # default success
        return True, "simulated_ok"
