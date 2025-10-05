from PyQt5.QtWidgets import QMainWindow, QTabWidget
from .tuning import TuningTab
from .torque_manager import TorqueManagerTab
from .security_manager import SecurityManagerTab
from .ecu_executor import ECUExecutorTab
from .dyno_simulator import DynoSimulatorTab

class MazdaUltimateTechnicianSuite(QMainWindow):
    """Dealer + Pro Level Mazda GUI"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mazda Ultimate Technician Suite – God Mode")
        self.setGeometry(50, 50, 1800, 1000)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.setup_tabs()

    def setup_tabs(self):
        self.tabs.addTab(TuningTab(), "🎯 Tuning")
        self.tabs.addTab(TorqueManagerTab(), "⚡ Torque Manager")
        self.tabs.addTab(SecurityManagerTab(), "🔐 Security")
        self.tabs.addTab(ECUExecutorTab(), "💻 ECU Executor")
        self.tabs.addTab(DynoSimulatorTab(), "📊 Dyno Simulator")
