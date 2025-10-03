# mazda_tool/ui/torque_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QCheckBox, QMessageBox
from mazda_tool.core.torque_manager import TorqueManager

class TorqueTab(QWidget):
    def __init__(self, parent=None, logger=print):
        super().__init__(parent)
        self.tm = TorqueManager(logger=logger)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>Torque Management & Wheel-Hop Protection</b>"))

        # Per-gear torque table (simple QTable)
        self.gear_table = QTableWidget(7, 2)  # gear 0..6, columns: gear, limit
        self.gear_table.setHorizontalHeaderLabels(["Gear", "Torque Limit (lb-ft)"])
        for i, gear in enumerate(range(0,7)):
            self.gear_table.setItem(i, 0, QTableWidgetItem(str(gear)))
            self.gear_table.setItem(i, 1, QTableWidgetItem(str(self.tm.get_gear_torque_limit(gear))))
        layout.addWidget(self.gear_table)

        # Apply gear limits btn
        apply_btn = QPushButton("Apply Gear Limits (Queue ECU Write)")
        apply_btn.clicked.connect(self._apply_table_limits)
        layout.addWidget(apply_btn)

        # Adaptive toggle & aggression
        adaptive_layout = QHBoxLayout()
        self.adaptive_checkbox = QCheckBox("Enable Adaptive Torque Mitigation")
        self.adaptive_checkbox.setChecked(self.tm.adaptive_enabled)
        self.adaptive_checkbox.stateChanged.connect(lambda s: self.tm.enable_adaptive(s == 2))
        adaptive_layout.addWidget(self.adaptive_checkbox)

        self.aggression_spin = QSpinBox()
        self.aggression_spin.setRange(0,100)
        self.aggression_spin.setValue(int(self.tm.adaptive_aggression * 100))
        self.aggression_spin.setSuffix("% Aggression")
        self.aggression_spin.valueChanged.connect(lambda val: self.tm.set_adaptive_aggression(val/100.0))
        adaptive_layout.addWidget(self.aggression_spin)

        layout.addLayout(adaptive_layout)

        # queued actions display
        layout.addWidget(QLabel("Queued ECU Actions (pending executor):"))
        self.queued_table = QTableWidget(1, 3)
        self.queued_table.setHorizontalHeaderLabels(["Index", "Action Type", "Status"])
        layout.addWidget(self.queued_table)

        refresh_btn = QPushButton("Refresh Queue")
        refresh_btn.clicked.connect(self._refresh_queue)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)
        self._refresh_queue()

    def _apply_table_limits(self):
        # read values from table and set them in TorqueManager (this queues ECU writes)
        for i in range(7):
            try:
                gear = int(self.gear_table.item(i, 0).text())
                val = float(self.gear_table.item(i, 1).text())
                self.tm.set_gear_torque_limit(gear, val)
            except Exception as e:
                QMessageBox.warning(self, "Invalid Value", f"Row {i} invalid: {e}")
                return
        QMessageBox.information(self, "Queued", "Gear torque limits queued for ECU update. Use executor to commit.")
        self._refresh_queue()

    def _refresh_queue(self):
        queued = self.tm.list_queued_actions()
        self.queued_table.setRowCount(max(1, len(queued)))
        for i, rec in enumerate(queued):
            self.queued_table.setItem(i, 0, QTableWidgetItem(str(i)))
            typ = rec["action"].get("type", "<unknown>")
            stat = rec.get("status", "queued")
            self.queued_table.setItem(i, 1, QTableWidgetItem(str(typ)))
            self.queued_table.setItem(i, 2, QTableWidgetItem(str(stat)))
