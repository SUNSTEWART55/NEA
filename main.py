"""
main.py

App entry point. Shows the login/signup screen; on success, routes
to the appropriate home page based on role.
"""

import customtkinter as ctk
from app.ui.auth_view import AuthView
from app.ui.teacher_ui.teacher_dashboard_view import TeacherDashboardView
from app.ui.student_ui.student_dashboard_view import StudentDashboardView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def center_window(window, width, height):
    """Position the window in the middle of the user's screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def on_login_success(user: dict):
    auth_view.pack_forget()

    if user["role"] == "teacher":
        home_view = TeacherDashboardView(app, user)
        home_view.pack(fill="both", expand=True)
    else:
        home_view = StudentDashboardView(app, user)
    home_view.pack(fill="both", expand=True)


app = ctk.CTk()
app.title("Maths Marking App")

WINDOW_WIDTH = 460
WINDOW_HEIGHT = 500
center_window(app, WINDOW_WIDTH, WINDOW_HEIGHT)
app.minsize(380, 440)  # stops the window becoming unusably small

auth_view = AuthView(app, on_login_success)
auth_view.pack(fill="both", expand=True)

app.mainloop()