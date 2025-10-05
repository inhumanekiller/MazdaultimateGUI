from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from muts_core.mazda_data_manager import MazdaDataManager

class TorqueManagerTab(QWidget):
    """Per-gear torque limits, SWAS overrides, boost cut removal"""
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Torque Manager Controls")
        self.layout.addWidget(self.label)

        self.apply_btn = QPushButton("Apply Torque Management")
        self.apply_btn.clicked.connect(self.apply_torque)
        self.layout.addWidget(self.apply_btn)

        self.data_manager = MazdaDataManager()

    def apply_torque(self):
        # Queue SWAS on/off, boost cut removal, per-gear torque adjustments
        self.data_manager.queue_action("SWAS_DISABLE")
        self.data_manager.queue_action("BOOST_CUT_1_2_GEAR_DISABLE")
        self.data_manager.queue_action("TORQUE_MAP_OPTIMIZE")
        self.label.setText("Queued torque management actions to ECU executor.")
