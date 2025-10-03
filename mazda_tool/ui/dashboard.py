# mazda_tool/ui/dashboard.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                             QLabel, QTabWidget, QHBoxLayout, QCheckBox)
from mazda_tool.core.data_manager import MazdaDataManager
from mazda_tool.simulators.dyno_simulator.py import DynoSimulator
import matplotlib.pyplot as plt

class MazdaUltimateDashboard(QMainWindow):
    """Ultimate Mazdaspeed 3 GUI"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mazda Ultimate Tuner")
        self.setGeometry(100, 100, 1200, 800)

        self.data_manager = MazdaDataManager()
        self.dyno_simulator = DynoSimulator()

        self._init_ui()

    def _init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Performance Tab
        self.performance_tab = QWidget()
        self.tabs.addTab(self.performance_tab, "Performance")

        perf_layout = QVBoxLayout()

        # SWAS toggle
        self.swas_checkbox = QCheckBox("SWAS Disable")
        self.swas_checkbox.setChecked(False)
        perf_layout.addWidget(self.swas_checkbox)

        # Boost Cut Removal toggle
        self.boost_cut_checkbox = QCheckBox("Remove Boost Cut 1st/2nd Gear")
        self.boost_cut_checkbox.setChecked(False)
        perf_layout.addWidget(self.boost_cut_checkbox)

        # Launch Control toggle
        self.launch_control_checkbox = QCheckBox("Launch Control Enabled")
        self.launch_control_checkbox.setChecked(False)
        perf_layout.addWidget(self.launch_control_checkbox)

        # Dyno Simulator button
        self.dyno_button = QPushButton("Run Dyno Simulation")
        self.dyno_button.clicked.connect(self.run_dyno)
        perf_layout.addWidget(self.dyno_button)

        # Status label
        self.status_label = QLabel("Status: Idle")
        perf_layout.addWidget(self.status_label)

        self.performance_tab.setLayout(perf_layout)

    def run_dyno(self):
        """Run dyno simulator with current settings"""
        boost = 18.5
        ignition_offset = 0

        if self.boost_cut_checkbox.isChecked():
            boost += 2  # Simulate boost removal effect
        if self.launch_control_checkbox.isChecked():
            ignition_offset += 3  # Simulate timing trick for launches

        rpm, hp, torque = self.dyno_simulator.simulate(boost_psi=boost, ignition_offset=ignition_offset)
        self.dyno_simulator.plot()
        self.status_label.setText(f"Dyno Complete: Peak HP ~{int(max(hp))} | Torque ~{int(max(torque))} lb-ft")


# Update mazda_tool/ui/dashboard.py
from mazda_tool.core.security import MazdaSecurityManager

# Inside MazdaUltimateDashboard.__init__():
self.security_manager = MazdaSecurityManager()
self.security_manager.security_status_changed.connect(self.update_security_status)

# Add Security Tab
self.security_tab = QWidget()
self.tabs.addTab(self.security_tab, "Security & Valet Mode")

sec_layout = QVBoxLayout()

# Valet Mode Toggle
self.valet_checkbox = QCheckBox("Enable Valet Mode")
self.valet_checkbox.stateChanged.connect(self.toggle_valet)
sec_layout.addWidget(self.valet_checkbox)

# Anti-Theft Disable Button
self.anti_theft_button = QPushButton("Disable Anti-Theft")
self.anti_theft_button.clicked.connect(self.disable_anti_theft)
sec_layout.addWidget(self.anti_theft_button)

# Status Label
self.security_status_label = QLabel("Security Status: Active")
sec_layout.addWidget(self.security_status_label)

self.security_tab.setLayout(sec_layout)

# Functions for callbacks
def toggle_valet(self, state):
    if state == 2:  # Checked
        self.security_manager.enable_valet_mode()
    else:
        self.security_manager.disable_valet_mode("1234")  # Default PIN for override

def disable_anti_theft(self):
    self.security_manager.disable_anti_theft("4321")

def update_security_status(self, message):
    self.security_status_label.setText(f"Security Status: {message}")
