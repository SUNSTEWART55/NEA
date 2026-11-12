"""
auth_view.py
 
Login / Sign-up screen. Toggles between the two modes in one frame.
Calls the app/data/*.py functions -- never talks to Supabase directly.
"""
 
import customtkinter as ctk
 
from app.data.users import (
    create_user, verify_login, username_exists,
    is_valid_password, PASSWORD_REQUIREMENTS_TEXT,
)
from app.data.schools_and_classes import (
    get_or_create_school, get_or_create_class,
    get_all_schools, get_classes_for_school,
)
from app.ui.responsive import make_responsive
 
 
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
        self.username_entry.bind("<FocusOut>", self.handle_username_focus_out)
 
        # Live feedback on username availability (signup only)
        self.username_status_label = ctk.CTkLabel(self, text="", font=("Arial", 11))
 
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=8)
 
        # Only shown in signup mode
        self.confirm_password_entry = ctk.CTkEntry(
            self, placeholder_text="Confirm password", show="*", width=250
        )
        self.password_requirements_label = ctk.CTkLabel(
            self, text=PASSWORD_REQUIREMENTS_TEXT,
            text_color="gray", font=("Arial", 11), justify="left"
        )
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email", width=250)
 
        # School/class as searchable dropdowns of existing records --
        # CTkComboBox still lets the user type a brand-new name.
        self.school_combo = ctk.CTkComboBox(
            self, values=[], width=250, command=self.handle_school_change
        )
        self.school_combo.set("")
        self.class_combo = ctk.CTkComboBox(self, values=[], width=250)
        self.class_combo.set("")
 
        self.role_menu = ctk.CTkOptionMenu(self, values=["student", "teacher"], command=self.handle_role_change)
        self.role_menu.set("student")
 
        self.error_label = ctk.CTkLabel(self, text="", text_color="red", wraplength=280, justify="left")
        self.error_label.pack(pady=(5, 0))
 
        self.submit_button = ctk.CTkButton(self, text="Log In", command=self.handle_submit)
        self.submit_button.pack(pady=15)
 
        self.toggle_button = ctk.CTkButton(
            self, text="Need an account? Sign up",
            fg_color="transparent", hover=False,
            command=self.toggle_mode
        )
        self.toggle_button.pack(pady=(0, 20))
 
        # Desktop-appropriate: Enter key submits the form from any field
        self.username_entry.bind("<Return>", lambda event: self.handle_submit())
        self.password_entry.bind("<Return>", lambda event: self.handle_submit())
        self.confirm_password_entry.bind("<Return>", lambda event: self.handle_submit())
 
        make_responsive(self, [
            (self.title_label, 22, None, None),
            (self.submit_button, 14, 250, 40),
            (self.toggle_button, 12, None, None),
        ])
 
    def toggle_mode(self):
        self.error_label.configure(text="")
        self.username_status_label.configure(text="")
        if self.mode == "login":
            self.mode = "signup"
            self.title_label.configure(text="Sign Up")
            self.submit_button.configure(text="Sign Up")
            self.toggle_button.configure(text="Already have an account? Log in")
 
            self.username_status_label.pack(after=self.username_entry)
            self.confirm_password_entry.pack(pady=8, after=self.password_entry)
            self.password_requirements_label.pack(pady=(0, 8), after=self.confirm_password_entry)
            self.email_entry.pack(pady=8, after=self.password_requirements_label)
            self.role_menu.pack(pady=8, after=self.email_entry)
 
            # Refresh the school list every time signup is opened
            self.school_combo.configure(values=[s["name"] for s in get_all_schools()])
            self.school_combo.pack(pady=8, after=self.role_menu)
            self.class_combo.pack(pady=8, after=self.school_combo)
            self.handle_role_change(self.role_menu.get())
 
            # work around a CustomTkinter quirk: an empty CTkEntry created
            self.confirm_password_entry.focus_set()
            self.email_entry.focus_set()
        else:
            self.mode = "login"
            self.title_label.configure(text="Log In")
            self.submit_button.configure(text="Log In")
            self.toggle_button.configure(text="Need an account? Sign up")
            self.username_status_label.pack_forget()
            self.confirm_password_entry.pack_forget()
            self.password_requirements_label.pack_forget()
            self.email_entry.pack_forget()
            self.role_menu.pack_forget()
            self.school_combo.pack_forget()
            self.class_combo.pack_forget()
 
    def handle_role_change(self, selected_role):
        # Class is only relevant for students -- hide it for teachers
        if selected_role == "student":
            self.class_combo.pack(pady=8, after=self.school_combo)
        else:
            self.class_combo.pack_forget()
 
    def handle_school_change(self, selected_school_name):
        # Repopulate the class dropdown to match whichever school is selected
        schools = get_all_schools()
        match = next((s for s in schools if s["name"] == selected_school_name), None)
        if match:
            classes = get_classes_for_school(match["id"])
            self.class_combo.configure(values=[c["name"] for c in classes])
        else:
            self.class_combo.configure(values=[])
        self.class_combo.set("")
 
    def handle_username_focus_out(self, event=None):
        if self.mode != "signup":
            return
        username = self.username_entry.get().strip()
        if not username:
            self.username_status_label.configure(text="")
            return
        if username_exists(username):
            self.username_status_label.configure(
                text="That username is taken -- please choose another.", text_color="orange"
            )
        else:
            self.username_status_label.configure(text="Username available.", text_color="green")
 
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
            confirm_password = self.confirm_password_entry.get().strip()
            email = self.email_entry.get().strip()
            role = self.role_menu.get()
            school_name = self.school_combo.get().strip()
            class_name = self.class_combo.get().strip()
 
            # Check the username first, before touching school/class records
            if username_exists(username):
                self.error_label.configure(text="That username is taken -- please choose another.")
                self.username_entry.focus_set()
                return
 
            if not is_valid_password(password):
                self.error_label.configure(text=PASSWORD_REQUIREMENTS_TEXT)
                return
 
            if password != confirm_password:
                self.error_label.configure(text="Passwords do not match.")
                return
 
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
