"""
student_dashboard_view.py
 
Landing page after student login: welcome message + navigation to
Personal Stats, Leaderboard, Homework, and Settings sections.
"""
 
import customtkinter as ctk
from app.ui.student_ui.student_stats_view import StudentStatsView
from app.ui.leaderboard_view import LeaderboardView
from app.ui.student_ui.student_homework_view import StudentHomeworkView
from app.ui.settings_view import SettingsView
from app.ui.responsive import make_responsive
 
 
class StudentDashboardView(ctk.CTkFrame):
    def __init__(self, master, user: dict, on_sign_out):
        super().__init__(master)
        self.master = master
        self.user = user
        self.on_sign_out = on_sign_out
 
        self.title_label = ctk.CTkLabel(
            self, text=f"Welcome, {user['username']}",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=(30, 25))
 
        self.stats_button = ctk.CTkButton(
            self, text="Personal Stats", width=220, height=45, command=self.open_stats
        )
        self.stats_button.pack(pady=8)
 
        self.leaderboard_button = ctk.CTkButton(
            self, text="Leaderboard", width=220, height=45, command=self.open_leaderboard
        )
        self.leaderboard_button.pack(pady=8)
 
        self.homework_button = ctk.CTkButton(
            self, text="Homework", width=220, height=45, command=self.open_homework
        )
        self.homework_button.pack(pady=8)
 
        self.settings_button = ctk.CTkButton(
            self, text="Settings", width=220, height=45, command=self.open_settings
        )
        self.settings_button.pack(pady=8)
 
        make_responsive(self, [
            (self.title_label, 24, None, None),
            (self.stats_button, 14, 220, 45),
            (self.leaderboard_button, 14, 220, 45),
            (self.homework_button, 14, 220, 45),
            (self.settings_button, 14, 220, 45),
        ])
 
    def open_stats(self):
        self.pack_forget()
        view = StudentStatsView(self.master, self.user, on_back=lambda: self.show_dashboard(view))
        view.pack(fill="both", expand=True)
 
    def open_leaderboard(self):
        self.pack_forget()
        view = LeaderboardView(self.master, self.user, on_back=lambda: self.show_dashboard(view))
        view.pack(fill="both", expand=True)
 
    def open_homework(self):
        self.pack_forget()
        view = StudentHomeworkView(self.master, self.user, on_back=lambda: self.show_dashboard(view))
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
