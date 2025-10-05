from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
import numpy as np

class DynoSimulatorTab(QWidget):
    """Simulated dyno run with torque/power curves"""
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Dyno Simulator")
        self.layout.addWidget(self.label)

        self.run_btn = QPushButton("Run Dyno Simulation")
        self.run_btn.clicked.connect(self.run_dyno)
        self.layout.addWidget(self.run_btn)

    def run_dyno(self):
        rpm = np.arange(1000, 7000, 500)
        torque = 250 + 50*np.sin(rpm/700)
        power = torque * rpm * 2 * np.pi / 5252
        self.label.setText(f"Simulated Peak Power: {int(max(power))} hp")
