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
# in your main window setup (e.g., mazda_tool/ui/dashboard.py or main_window.py)
from mazda_tool.ui.torque_tab import TorqueTab

# create and add the torque tab
self.torque_tab = TorqueTab(logger=self._ui_logger)
self.tabs.addTab(self.torque_tab, "🛞 Torque Mgmt")
# in your main GUI file where you have self.tabs
from mazda_tool.ui.executor_tab import ExecutorTab

# Provide two functions from your manager(s):
# Example if you have a TorqueManager instance self.torque_manager:
# queue_provider = lambda: list(self.torque_manager.list_queued_actions())
# mark_done = lambda idx, success, msg: self.torque_manager.mark_action_done(idx, success, msg)

# If you have multiple managers, you may want to aggregate queued actions:
def combined_queue_provider():
    # example aggregator - adjust to your implementations
    q = []
    try:
        q.extend(self.torque_tab.tm.list_queued_actions())
    except Exception:
        pass
    try:
        q.extend(self.security_tab.sm.list_queued_actions())
    except Exception:
        pass
    # NOTE: aggregated queues must be consistent indices for mark_done; easier is to use one executor per manager
    return q

# For simplicity, attach an executor to TorqueManager only:
queue_provider = lambda: list(self.torque_tab.tm.list_queued_actions())
mark_done = lambda idx, success, msg: self.torque_tab.tm.mark_action_done(idx, success, msg)

self.executor_tab = ExecutorTab(queue_provider=queue_provider, mark_done=mark_done)
self.tabs.addTab(self.executor_tab, "🔁 Executor")
