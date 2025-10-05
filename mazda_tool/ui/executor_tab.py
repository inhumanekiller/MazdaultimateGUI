# mazda_tool/ui/executor_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QTimer
from mazda_tool.core.executor import ECUExecutor
from typing import Callable

class ExecutorTab(QWidget):
    def __init__(self, queue_provider: Callable[[], list], mark_done: Callable[[int, bool, str], bool], parent=None):
        super().__init__(parent)
        self.queue_provider = queue_provider
        self.mark_done = mark_done

        self.executor = ECUExecutor(queue_provider=self.queue_provider, mark_done=self.mark_done, mode="simulation")
        self._init_ui()

        # Timer to refresh queued actions table
        self.timer = QTimer(self)
        self.timer.setInterval(1200)
        self.timer.timeout.connect(self._refresh_table)
        self.timer.start()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>ECU Executor</b> (Simulation mode)"))

        # Mode selector (simulation/hardware)
        self.mode_select = QComboBox()
        self.mode_select.addItems(["simulation", "hardware"])
        self.mode_select.currentTextChanged.connect(self._mode_changed)
        layout.addWidget(QLabel("Executor Mode"))
        layout.addWidget(self.mode_select)

        # Start/Stop buttons
        self.start_btn = QPushButton("Start Executor")
        self.stop_btn = QPushButton("Stop Executor")
        self.start_btn.clicked.connect(self._start_executor)
        self.stop_btn.clicked.connect(self._stop_executor)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        # Queued actions table
        self.queue_table = QTableWidget(1, 4)
        self.queue_table.setHorizontalHeaderLabels(["Idx", "Type", "Status", "Queued At"])
        layout.addWidget(self.queue_table)

        self.setLayout(layout)
        self._refresh_table()

    def _mode_changed(self, mode: str):
        # swap executor mode (will restart if running)
        was_running = self.executor.is_running()
        if was_running:
            self.executor.stop()
        self.executor = ECUExecutor(queue_provider=self.queue_provider, mark_done=self.mark_done, mode=mode)
        if was_running:
            self.executor.start()

    def _start_executor(self):
        if not self.executor.is_running():
            self.executor.start()
            QMessageBox.information(self, "Executor", "Executor started")
        else:
            QMessageBox.information(self, "Executor", "Executor already running")

    def _stop_executor(self):
        if self.executor.is_running():
            self.executor.stop()
            QMessageBox.information(self, "Executor", "Executor stopped")
        else:
            QMessageBox.information(self, "Executor", "Executor not running")

    def _refresh_table(self):
        queue = self.queue_provider() or []
        self.queue_table.setRowCount(max(1, len(queue)))
        for i, rec in enumerate(queue):
            self.queue_table.setItem(i, 0, QTableWidgetItem(str(i)))
            self.queue_table.setItem(i, 1, QTableWidgetItem(str(rec.get("action", {}).get("type", "<unknown>"))))
            self.queue_table.setItem(i, 2, QTableWidgetItem(str(rec.get("status", "<no-status>"))))
            self.queue_table.setItem(i, 3, QTableWidgetItem(str(rec.get("queued_at", ""))))

