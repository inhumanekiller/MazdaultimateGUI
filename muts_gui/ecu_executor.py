#from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from muts_core.mazda_data_manager import MazdaDataManager

class ECUExecutorTab(QWidget):
    """Direct ECU writing / simulation executor"""
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("ECU Executor (Simulation Mode)")
        self.layout.addWidget(self.label)

        self.execute_btn = QPushButton("Run Queued ECU Actions")
        self.execute_btn.clicked.connect(self.execute_actions)
        self.layout.addWidget(self.execute_btn)

        # Core data manager instance
        self.data_manager = MazdaDataManager()

    def execute_actions(self):
        # In simulation, print actions
        results = self.data_manager.execute_queued_actions()
        self.label.setText(f"Executed actions: {results}")
