"""
settings_view.py
 
Shared settings page for both students and teachers: sign out,
change account details (email/password/school/class), and delete
account. Used by both TeacherDashboardView and StudentDashboardView,
so it lives at app/ui/ rather than under teacher_ui/ or student_ui/.
"""
 
import customtkinter as ctk
from tkinter import messagebox
 
from app.data.users import update_user, delete_user, is_valid_password, PASSWORD_REQUIREMENTS_TEXT
from app.data.schools_and_classes import (
    get_or_create_school, get_or_create_class,
    get_all_schools, get_classes_for_school,
    get_school_by_id, get_class_by_id,
)
from app.ui.responsive import make_responsive
 
 
class SettingsView(ctk.CTkFrame):
    def __init__(self, master, user: dict, on_back, on_sign_out):
        """
        on_back: return to the caller's dashboard without signing out.
        on_sign_out: called after a sign-out OR an account deletion --
        the caller is responsible for showing the login screen again.
        """
        super().__init__(master)
        self.master = master
        self.user = user
        self.on_back = on_back
        self.on_sign_out = on_sign_out
 
        # Back is context-aware: while the change-details form is open it
        # cancels the edit and returns to this main settings view; otherwise
        # it leaves settings entirely and returns to the dashboard.
        self.back_button = ctk.CTkButton(self, text="< Back", width=90, command=self.handle_back)
        self.back_button.pack(anchor="nw", padx=15, pady=(15, 0))
 
        self.title_label = ctk.CTkLabel(self, text="Settings", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=(20, 30))
 
        self.change_details_button = ctk.CTkButton(
            self, text="Change Details", width=220, height=45, command=self.open_change_details
        )
        self.change_details_button.pack(pady=10)
 
        self.sign_out_button = ctk.CTkButton(
            self, text="Sign Out", width=220, height=45, command=self.handle_sign_out
        )
        self.sign_out_button.pack(pady=10)
 
        self.delete_button = ctk.CTkButton(
            self, text="Delete Account", width=220, height=45,
            fg_color="darkred", hover_color="#8b0000",
            command=self.handle_delete_account
        )
        self.delete_button.pack(pady=10)
 
        # -- Change-details form, hidden until "Change Details" is pressed --
        self.details_frame = ctk.CTkFrame(self, fg_color="transparent")
 
        self.email_entry = ctk.CTkEntry(self.details_frame, placeholder_text="Email", width=250)
        self.email_entry.pack(pady=8)
 
        self.school_combo = ctk.CTkComboBox(
            self.details_frame, values=[], width=250, command=self.handle_school_change
        )
        self.school_combo.pack(pady=8)
 
        self.class_combo = ctk.CTkComboBox(self.details_frame, values=[], width=250)
        if self.user.get("role") == "student":
            self.class_combo.pack(pady=8)
 
        self.new_password_entry = ctk.CTkEntry(
            self.details_frame, placeholder_text="New password (leave blank to keep current)",
            show="*", width=250
        )
        self.new_password_entry.pack(pady=8)
 
        self.confirm_new_password_entry = ctk.CTkEntry(
            self.details_frame, placeholder_text="Confirm new password", show="*", width=250
        )
        self.confirm_new_password_entry.pack(pady=8)
 
        self.password_requirements_label = ctk.CTkLabel(
            self.details_frame, text=PASSWORD_REQUIREMENTS_TEXT,
            text_color="gray", font=("Arial", 11), justify="left"
        )
        self.password_requirements_label.pack(pady=(0, 8))
 
        self.details_error_label = ctk.CTkLabel(
            self.details_frame, text="", text_color="red", wraplength=280, justify="left"
        )
        self.details_error_label.pack(pady=(0, 8))
 
        self.save_details_button = ctk.CTkButton(
            self.details_frame, text="Save Changes", command=self.handle_save_details
        )
        self.save_details_button.pack(pady=8)
 
        # Values as they were when "Change Details" was opened, so Back can
        # discard unsaved edits instead of leaving stale text on screen.
        self._original_email = ""
        self._original_school_name = ""
        self._original_class_name = ""
 
        make_responsive(self, [
            (self.title_label, 24, None, None),
            (self.change_details_button, 14, 220, 45),
            (self.sign_out_button, 14, 220, 45),
            (self.delete_button, 14, 220, 45),
            (self.password_requirements_label, 11, None, None),
            (self.details_error_label, 12, None, None),
            (self.save_details_button, 14, 220, 40),
        ])
 
    def open_change_details(self):
        # Snapshot current values -- restored if the user backs out
        self._original_email = self.user.get("email", "")
 
        school = get_school_by_id(self.user["school_id"]) if self.user.get("school_id") else None
        self._original_school_name = school["name"] if school else ""
 
        class_obj = get_class_by_id(self.user["class_id"]) if self.user.get("class_id") else None
        self._original_class_name = class_obj["name"] if class_obj else ""
 
        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, self._original_email)
 
        self.school_combo.configure(values=[s["name"] for s in get_all_schools()])
        self.school_combo.set(self._original_school_name)
        self._refresh_class_options(self._original_school_name)
        self.class_combo.set(self._original_class_name)
 
        self.new_password_entry.delete(0, "end")
        self.confirm_new_password_entry.delete(0, "end")
        self.details_error_label.configure(text="")
 
        self.change_details_button.pack_forget()
        self.sign_out_button.pack_forget()
        self.delete_button.pack_forget()
        self.details_frame.pack(pady=10)
 
        # work around a CustomTkinter quirk: an empty CTkEntry that was cycling focus through the empty fields forces them to redraw
        self.new_password_entry.focus_set()
        self.confirm_new_password_entry.focus_set()
        self.details_frame.focus_set()
 
    def close_change_details(self):
        """Hide the form and go back to the main settings buttons, discarding
        any unsaved edits (nothing in it was ever written to the database)."""
        self.details_frame.pack_forget()
        self.change_details_button.pack(pady=10)
        self.sign_out_button.pack(pady=10)
        self.delete_button.pack(pady=10)
 
    def handle_back(self):
        if self.details_frame.winfo_ismapped():
            self.close_change_details()
        else:
            self.on_back()
 
    def handle_school_change(self, selected_school_name):
        self._refresh_class_options(selected_school_name)
        self.class_combo.set("")
 
    def _refresh_class_options(self, school_name):
        schools = get_all_schools()
        match = next((s for s in schools if s["name"] == school_name), None)
        if match:
            classes = get_classes_for_school(match["id"])
            self.class_combo.configure(values=[c["name"] for c in classes])
        else:
            self.class_combo.configure(values=[])
 
    def handle_save_details(self):
        email = self.email_entry.get().strip()
        school_name = self.school_combo.get().strip()
        class_name = self.class_combo.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_new_password = self.confirm_new_password_entry.get().strip()
 
        if not school_name:
            self.details_error_label.configure(text="School is required.")
            return
        if self.user.get("role") == "student" and not class_name:
            self.details_error_label.configure(text="Class is required for students.")
            return
 
        fields = {}
        if email and email != self.user.get("email"):
            fields["email"] = email
 
        if new_password or confirm_new_password:
            if not is_valid_password(new_password):
                self.details_error_label.configure(text=PASSWORD_REQUIREMENTS_TEXT)
                return
            if new_password != confirm_new_password:
                self.details_error_label.configure(text="Passwords do not match.")
                return
            fields["password"] = new_password
 
        try:
            school = get_or_create_school(school_name)
            if school["id"] != self.user.get("school_id"):
                fields["school_id"] = school["id"]
 
            if self.user.get("role") == "student":
                class_obj = get_or_create_class(school["id"], class_name)
                if class_obj["id"] != self.user.get("class_id"):
                    fields["class_id"] = class_obj["id"]
        except Exception as e:
            self.details_error_label.configure(text=f"Could not update school/class: {e}")
            return
 
        if not fields:
            self.details_error_label.configure(text="Nothing to update.")
            return
 
        confirmed = messagebox.askyesno("Save Changes", "Save these changes to your account?")
        if not confirmed:
            return
 
        try:
            updated_user = update_user(self.user["id"], **fields)
        except ValueError as e:
            self.details_error_label.configure(text=str(e))
            return
 
        self.user.update(updated_user)
        self.close_change_details()
        messagebox.showinfo("Settings", "Your details have been updated.")
 
    def handle_sign_out(self):
        self.on_sign_out()
 
    def handle_delete_account(self):
        confirmed = messagebox.askyesno(
            "Delete Account",
            "This will permanently delete your account and cannot be undone. Continue?"
        )
        if not confirmed:
            return
        delete_user(self.user["id"])
        self.on_sign_out()
