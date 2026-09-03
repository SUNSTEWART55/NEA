"""
student_dashboard_view.py

Landing page after student login: welcome message + navigation to
Personal Stats, Leaderboard, and Homework sections.
"""

import customtkinter as ctk
from app.ui.student_ui.student_stats_view import StudentStatsView
from app.ui.leaderboard_view import LeaderboardView
from app.ui.student_ui.student_homework_view import StudentHomeworkView


class StudentDashboardView(ctk.CTkFrame):
    def __init__(self, master, user: dict):
        super().__init__(master)
        self.master = master
        self.user = user

        self.title_label = ctk.CTkLabel(
            self, text=f"Welcome, {user['username']}",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=(30, 25))

        ctk.CTkButton(self, text="Personal Stats", width=220, height=45, command=self.open_stats).pack(pady=8)
        ctk.CTkButton(self, text="Leaderboard", width=220, height=45, command=self.open_leaderboard).pack(pady=8)
        ctk.CTkButton(self, text="Homework", width=220, height=45, command=self.open_homework).pack(pady=8)

    def open_stats(self):
        self.pack_forget()
        StudentStatsView(self.master, self.user, on_back=self.show_dashboard).pack(fill="both", expand=True)

    def open_leaderboard(self):
        self.pack_forget()
        LeaderboardView(self.master, self.user, on_back=self.show_dashboard).pack(fill="both", expand=True)

    def open_homework(self):
        self.pack_forget()
        StudentHomeworkView(self.master, self.user, on_back=self.show_dashboard).pack(fill="both", expand=True)

    def show_dashboard(self):
        self.pack(fill="both", expand=True)