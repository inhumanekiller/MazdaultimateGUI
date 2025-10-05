## mazda_tool/__main__.py
import sys
from PyQt5.QtWidgets import QApplication, QTabWidget, QMainWindow
from mazda_tool.ui.torque_tab import TorqueTab
from mazda_tool.ui.executor_tab import ExecutorTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mazda Performance Suite")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Torque Manager tab
        self.torque_tab = TorqueTab()
        self.tabs.addTab(self.torque_tab, "⚡ Torque Manager")

        # Executor tab (hooks into torque manager)
        queue_provider = lambda: list(self.torque_tab.tm.list_queued_actions())
        mark_done = lambda idx, success, msg: self.torque_tab.tm.mark_action_done(idx, success, msg)

        self.executor_tab = ExecutorTab(
            queue_provider=queue_provider,
            mark_done=mark_done
        )
        self.tabs.addTab(self.executor_tab, "🔁 Executor")

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

