from typing import List, Dict, Any
import reflex as rx


class State(rx.State):
    # Auth
    token: str = ""
    is_authenticated: bool = True
    user_id: int = 1
    user_name: str = "Dr. Alexander Wright"
    user_role: str = "admin"  # "admin", "doctor", "receptionist", "patient"
    user_email: str = "admin@hospital.com"
    login_email: str = "admin@hospital.com"
    login_password: str = "admin123"
    login_error: str = ""

    # Navigation
    active_page: str = "dashboard"

    # Dashboard Data
    total_patients: int = 20
    today_appointments: int = 4
    revenue_today: float = 1420.0
    revenue_this_month: float = 18450.0
    active_prescriptions: int = 10
    low_stock_count: int = 2
    pending_reports: int = 5
    
    # Toast Notification
    toast_message: str = ""
    toast_type: str = "success"  # "success", "error", "warning"
    show_toast: bool = False

    def set_role(self, role: str):
        self.user_role = role

    def show_notification(self, message: str, n_type: str = "success"):
        self.toast_message = message
        self.toast_type = n_type
        self.show_toast = True

    def dismiss_toast(self):
        self.show_toast = False

    def login(self):
        if not self.login_email or not self.login_password:
            self.login_error = "Please provide email and password"
            return
        self.is_authenticated = True
        self.login_error = ""
        self.show_notification("Successfully logged in!")
        return rx.redirect("/dashboard")

    def logout(self):
        self.token = ""
        self.is_authenticated = False
        return rx.redirect("/login")
