"""
auth_view.py

Login / Sign-up screen. Toggles between the two modes in one frame.
Calls the app/data/*.py functions -- never talks to Supabase directly.
"""

import customtkinter as ctk
from app.data.users import create_user, verify_login
from app.data.schools_and_classes import get_or_create_school, get_or_create_class


class AuthView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        """
        on_login_success: a callback function that receives the
        logged-in user's dict (id, username, role, etc) once
        login succeeds. The main window decides what to do next.
        """
        super().__init__(master)
        self.on_login_success = on_login_success
        self.mode = "login"  # or "signup"

        self.title_label = ctk.CTkLabel(self, text="Log In", font=("Arial", 22, "bold"))
        self.title_label.pack(pady=(30, 10))

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=250)
        self.username_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=8)

        # Only shown in signup mode
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email", width=250)
        self.school_entry = ctk.CTkEntry(self, placeholder_text="School name", width=250)
        self.class_entry = ctk.CTkEntry(self, placeholder_text="Class (students only)", width=250)

        self.role_menu = ctk.CTkOptionMenu(self, values=["student", "teacher"], command=self.handle_role_change)
        self.role_menu.set("student")

        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack(pady=(5, 0))

        self.submit_button = ctk.CTkButton(self, text="Log In", command=self.handle_submit)
        self.submit_button.pack(pady=15)

        self.toggle_button = ctk.CTkButton(
            self, text="Need an account? Sign up",
            fg_color="transparent", hover=False,
            command=self.toggle_mode
        )
        self.toggle_button.pack(pady=(0, 20))

        # Desktop-appropriate: Enter key submits the form from either field
        self.username_entry.bind("<Return>", lambda event: self.handle_submit())
        self.password_entry.bind("<Return>", lambda event: self.handle_submit())

    def toggle_mode(self):
        self.error_label.configure(text="")
        if self.mode == "login":
            self.mode = "signup"
            self.title_label.configure(text="Sign Up")
            self.submit_button.configure(text="Sign Up")
            self.toggle_button.configure(text="Already have an account? Log in")
            self.email_entry.pack(pady=8, after=self.password_entry)
            self.role_menu.pack(pady=8, after=self.email_entry)
            self.school_entry.pack(pady=8, after=self.role_menu)
            self.class_entry.pack(pady=8, after=self.school_entry)
            self.handle_role_change(self.role_menu.get())
        else:
            self.mode = "login"
            self.title_label.configure(text="Log In")
            self.submit_button.configure(text="Log In")
            self.toggle_button.configure(text="Need an account? Sign up")
            self.email_entry.pack_forget()
            self.role_menu.pack_forget()
            self.school_entry.pack_forget()
            self.class_entry.pack_forget()

    def handle_role_change(self, selected_role):
        # Class is only relevant for students -- hide it for teachers
        if selected_role == "student":
            self.class_entry.pack(pady=8, after=self.school_entry)
        else:
            self.class_entry.pack_forget()

    def handle_submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text="Username and password are required.")
            return

        if self.mode == "login":
            user = verify_login(username, password)
            if user is None:
                self.error_label.configure(text="Incorrect username or password.")
                return
            self.on_login_success(user)

        else:  # signup
            email = self.email_entry.get().strip()
            role = self.role_menu.get()
            school_name = self.school_entry.get().strip()
            class_name = self.class_entry.get().strip()

            if not email or not school_name:
                self.error_label.configure(text="Email and school are required.")
                return

            if role == "student" and not class_name:
                self.error_label.configure(text="Class is required for students.")
                return

            try:
                school = get_or_create_school(school_name)
                class_obj = None
                if role == "student":
                    class_obj = get_or_create_class(school["id"], class_name)

                user = create_user(
                    username, password, email, role,
                    school_id=school["id"],
                    class_id=class_obj["id"] if class_obj else None,
                )
            except ValueError as e:
                self.error_label.configure(text=str(e))
                return

            self.on_login_success(user)