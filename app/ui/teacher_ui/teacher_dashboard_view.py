"""
teacher_dashboard_view.py

Landing page after teacher login: welcome message + navigation
to Homework and Statistics sections.
"""

import customtkinter as ctk
from app.ui.teacher_ui.teacher_homework_view import TeacherHomeworkView
from app.ui.teacher_ui.teacher_statistics_view import TeacherStatisticsView


class TeacherDashboardView(ctk.CTkFrame):
    def __init__(self, master, user: dict):
        super().__init__(master)
        self.master = master
        self.user = user

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

    def open_homework(self):
        self.pack_forget()
        view = TeacherHomeworkView(self.master, self.user, on_back=self.show_dashboard)
        view.pack(fill="both", expand=True)

    def open_statistics(self):
        self.pack_forget()
        view = TeacherStatisticsView(self.master, self.user, on_back=self.show_dashboard)
        view.pack(fill="both", expand=True)

    def show_dashboard(self):
        self.pack(fill="both", expand=True)