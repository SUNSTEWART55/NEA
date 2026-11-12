"""
teacher_dashboard_view.py
 
Landing page after teacher login: welcome message + navigation
to Homework, Statistics, and Settings sections.
"""
 
import customtkinter as ctk
from app.ui.teacher_ui.teacher_homework_view import TeacherHomeworkView
from app.ui.teacher_ui.teacher_statistics_view import TeacherStatisticsView
from app.ui.settings_view import SettingsView
from app.ui.responsive import make_responsive
 
 
class TeacherDashboardView(ctk.CTkFrame):
    def __init__(self, master, user: dict, on_sign_out):
        super().__init__(master)
        self.master = master
        self.user = user
        self.on_sign_out = on_sign_out
 
        self.title_label = ctk.CTkLabel(
            self, text=f"Welcome, {user['username']}",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=(40, 30))
 
        self.homework_button = ctk.CTkButton(
            self, text="Homework", width=220, height=45,
            command=self.open_homework
        )
        self.homework_button.pack(pady=10)
 
        self.stats_button = ctk.CTkButton(
            self, text="Homework Statistics", width=220, height=45,
            command=self.open_statistics
        )
        self.stats_button.pack(pady=10)
 
        self.settings_button = ctk.CTkButton(
            self, text="Settings", width=220, height=45,
            command=self.open_settings
        )
        self.settings_button.pack(pady=10)
 
        make_responsive(self, [
            (self.title_label, 24, None, None),
            (self.homework_button, 14, 220, 45),
            (self.stats_button, 14, 220, 45),
            (self.settings_button, 14, 220, 45),
        ])
 
    def open_homework(self):
        self.pack_forget()
        view = TeacherHomeworkView(self.master, self.user, on_back=lambda: self.show_dashboard(view))
        view.pack(fill="both", expand=True)
 
    def open_statistics(self):
        self.pack_forget()
        view = TeacherStatisticsView(self.master, self.user, on_back=lambda: self.show_dashboard(view))
        view.pack(fill="both", expand=True)
 
    def open_settings(self):
        self.pack_forget()
        view = SettingsView(
            self.master, self.user,
            on_back=lambda: self.show_dashboard(view), on_sign_out=self.on_sign_out
        )
        view.pack(fill="both", expand=True)
 
    def show_dashboard(self, previous_view=None):
        # Remove whichever sub-view called us back, so it doesn't stay
        # packed underneath the dashboard once we're shown again.
        if previous_view is not None:
            previous_view.destroy()
        self.pack(fill="both", expand=True)
