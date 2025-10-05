from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from muts_core.mazda_data_manager import MazdaDataManager

class SecurityManagerTab(QWidget):
    """Valet, immobilizer, anti-theft"""
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Security Controls")
        self.layout.addWidget(self.label)

        self.enable_valet = QPushButton("Enable Valet Mode")
        self.enable_valet.clicked.connect(self.enable_valet_mode)
        self.layout.addWidget(self.enable_valet)

        self.data_manager = MazdaDataManager()

    def enable_valet_mode(self):
        self.data_manager.queue_action("ENABLE_VALET_MODE")
        self.label.setText("Valet Mode queued for ECU execution.")
