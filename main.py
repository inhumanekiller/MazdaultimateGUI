# main.py
from PyQt5.QtWidgets import QApplication
from muts_gui.dashboard import MazdaUltimateTechnicianSuite
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MazdaUltimateTechnicianSuite()
    window.show()
    sys.exit(app.exec_())

