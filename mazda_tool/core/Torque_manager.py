# mazda_tool/core/torque_manager.py
import time
import threading
from typing import Dict, Any, List
from collections import deque
from datetime import datetime

class TorqueManager:
    """
    God-level Torque Management for Mazdaspeed 3
    - per-gear torque limits
    - adaptive torque intervention on wheel slip/wheelhop
    - temporary timing reduction as mitigation
    - safe queuing of ECU changes (executor required to actually write)
    """

    def __init__(self, logger=None):
        # default torque limits (crank lb-ft equivalent approximations)
        # keys are gear numbers as integers; 0 = neutral/all
        self.gear_torque_limits: Dict[int, float] = {
            0: 360.0,  # global default cap
            1: 300.0,
            2: 320.0,
            3: 360.0,
            4: 360.0,
            5: 360.0,
            6: 360.0
        }

        # runtime flags
        self.adaptive_enabled = True
        self.adaptive_aggression = 0.6  # 0-1, how aggressively to clamp torque when slip detected
        self.timing_reduction_enabled = True
        self.timing_reduction_deg = 3.0  # degrees BTDC to temporarily remove

        # safety queues for ECU writes (must be executed by authorized executor)
        self.queued_actions: deque = deque(maxlen=200)

        # short event history for slip/knock events
        self.event_history: deque = deque(maxlen=500)

        # small logger stub
        self.logger = logger or (lambda *args, **kwargs: None)

        # lock for thread-safety
        self._lock = threading.RLock()

    # ---------- Public API ----------
    def set_gear_torque_limit(self, gear: int, torque_lbft: float):
        """Set per-gear torque limit (in lb-ft). Use gear=0 for global default."""
        with self._lock:
            self.gear_torque_limits[int(gear)] = float(torque_lbft)
            self._audit("SET_GEAR_LIMIT", {"gear": gear, "limit": torque_lbft})
            # queue ECU mapping update (do not write immediately)
            self._queue_ecu_update({"type": "gear_torque_limit", "gear": gear, "value": torque_lbft})

    def get_gear_torque_limit(self, gear: int) -> float:
        """Return the current torque limit for gear (fall back to global)"""
        with self._lock:
            return float(self.gear_torque_limits.get(int(gear), self.gear_torque_limits.get(0, 360.0)))

    def enable_adaptive(self, enable: bool):
        with self._lock:
            self.adaptive_enabled = bool(enable)
            self._audit("ADAPTIVE_SET", {"enabled": self.adaptive_enabled})

    def set_adaptive_aggression(self, level: float):
        """level between 0.0 (gentle) and 1.0 (aggressive torque clamp)"""
        with self._lock:
            self.adaptive_aggression = max(0.0, min(1.0, float(level)))
            self._audit("ADAPTIVE_AGGRESSION", {"level": self.adaptive_aggression})

    # ---------- Event Processing ----------
    def process_wheel_slip_event(self, timestamp: float, gear: int, wheel_slip_percent: float, rpm: int, boost: float):
        """
        Called by the data layer when wheel slip / hop is detected.
        If adaptive mitigation is enabled, create a mitigation action (timing reduction + torque clamp).
        """
        with self._lock:
            entry = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "type": "wheel_slip",
                "gear": int(gear),
                "slip_pct": float(wheel_slip_percent),
                "rpm": int(rpm),
                "boost": float(boost)
            }
            self.event_history.append(entry)
            self.logger("TorqueManager: Wheel slip event", entry)

            # decision threshold (tunable): if slip_pct > 12% treat as significant
            if self.adaptive_enabled and wheel_slip_percent > 12.0:
                # calculate a temporary clamp: reduce torque to some fraction of gear limit
                base_limit = self.get_gear_torque_limit(int(gear))
                clamp_factor = 1.0 - (self.adaptive_aggression * min(0.8, (wheel_slip_percent / 100.0) * 2.0))
                new_limit = max(100.0, base_limit * clamp_factor)  # never go below 100 lb-ft fallback
                self._audit("ADAPTIVE_CLAMP", {"gear": gear, "old_limit": base_limit, "new_limit": new_limit, "slip_pct": wheel_slip_percent})
                # queue ECU action to apply this temporary clamp for safety
                self._queue_ecu_update({
                    "type": "temp_gear_clamp",
                    "gear": gear,
                    "value": new_limit,
                    "expires_at": time.time() + 6  # auto-expire after 6 seconds
                })
                # optionally schedule a temporary timing reduction
                if self.timing_reduction_enabled:
                    self._queue_ecu_update({
                        "type": "temp_timing_reduction",
                        "deg": self.timing_reduction_deg,
                        "expires_at": time.time() + 6
                    })

    def process_knock_event(self, timestamp: float, cylinder: int, knock_level: float, rpm: int):
        """Process a knock event. If recurring, create more conservative actions."""
        with self._lock:
            entry = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "type": "knock",
                "cylinder": int(cylinder),
                "knock_level": float(knock_level),
                "rpm": int(rpm)
            }
            self.event_history.append(entry)
            self.logger("TorqueManager: Knock event", entry)

            # If many knocks in short period, be aggressive
            recent_knocks = [e for e in list(self.event_history)[-30:] if e["type"] == "knock"]
            if len(recent_knocks) >= 3:
                # apply immediate temporary timing reduction and torque clamp
                self._audit("KNOCK_MITIGATION", {"count": len(recent_knocks)})
                self._queue_ecu_update({"type": "temp_timing_reduction", "deg": 4.0, "reason": "knock", "expires_at": time.time() + 8})
                self._queue_ecu_update({"type": "temp_global_torque_clamp", "value": 0.85 * self.gear_torque_limits.get(0, 360.0), "reason": "knock", "expires_at": time.time() + 8})

    # ---------- Queuing & Executor Hooks ----------
    def _queue_ecu_update(self, action: Dict[str, Any]):
        """Queue a safe ECU update. Actual execution must be done by authorized executor."""
        with self._lock:
            action_record = {
                "queued_at": time.time(),
                "status": "queued",
                "action": action
            }
            self.queued_actions.append(action_record)
            self._audit("QUEUE_ACTION", {"action": action})
            # Also log to logger for UI notification
            self.logger("TorqueManager: queued_action", action_record)

    def list_queued_actions(self) -> List[Dict[str, Any]]:
        return list(self.queued_actions)

    def mark_action_done(self, index: int, success: bool, message: str = ""):
        """Mark queued action complete or failed (executor should call this)."""
        with self._lock:
            idx = int(index)
            if 0 <= idx < len(self.queued_actions):
                rec = self.queued_actions[idx]
                rec["status"] = "done" if success else "failed"
                rec["done_at"] = time.time()
                rec["message"] = message
                self._audit("ACTION_DONE", {"index": idx, "success": success, "msg": message})
                return True
            return False

    # ---------- Auditing ----------
    def _audit(self, event: str, meta: Dict[str, Any]):
        """Keep internal audit trail (could hook to external logger/db)"""
        msg = {"ts": datetime.utcnow().isoformat() + "Z", "event": event, "meta": meta}
        # append to event history for now
        try:
            self.event_history.append(msg)
        except Exception:
            pass
        self.logger("TorqueManager: audit", msg)
