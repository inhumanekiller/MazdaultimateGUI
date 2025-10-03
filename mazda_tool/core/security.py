## mazda_tool/core/security.py
from PyQt5.QtCore import QObject, pyqtSignal

class MazdaSecurityManager(QObject):
    """Factory-level Security & Valet Mode for Mazdaspeed 3"""
    
    security_status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.valet_mode_enabled = False
        self.anti_theft_enabled = True
        self.max_speed_valet = 50  # mph
        self.max_rpm_valet = 4000
        self.max_torque_valet = 250  # lb-ft

    def enable_valet_mode(self, speed_limit=50, rpm_limit=4000, torque_limit=250):
        self.valet_mode_enabled = True
        self.max_speed_valet = speed_limit
        self.max_rpm_valet = rpm_limit
        self.max_torque_valet = torque_limit
        self.security_status_changed.emit("Valet Mode Enabled")
    
    def disable_valet_mode(self, pin_code):
        if pin_code == "1234":  # Factory override PIN, can be changed
            self.valet_mode_enabled = False
            self.security_status_changed.emit("Valet Mode Disabled")
        else:
            self.security_status_changed.emit("Invalid PIN: Valet Mode remains enabled")
    
    def check_start_permission(self):
        """Check if engine can start"""
        if self.anti_theft_enabled:
            return False
        return True

    def disable_anti_theft(self, pin_code):
        if pin_code == "4321":  # Factory override PIN
            self.anti_theft_enabled = False
            self.security_status_changed.emit("Anti-Theft Disabled")
        else:
            self.security_status_changed.emit("Invalid PIN: Anti-Theft remains active")

