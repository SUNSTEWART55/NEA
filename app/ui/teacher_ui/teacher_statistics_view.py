"""
teacher_statistics_view.py

Statistics section: a table of student performance per question,
filterable by class and individual student across the whole school.
"""

import customtkinter as ctk
from app.data.schools_and_classes import get_classes_for_school, get_students_for_school
from app.data.statistics import get_performance_rows


class TeacherStatisticsView(ctk.CTkFrame):
    def __init__(self, master, user: dict, on_back):
        super().__init__(master)
        self.user = user
        self.on_back = on_back
        self.school_id = user["school_id"]

        self.back_button = ctk.CTkButton(self, text="< Back", width=80, command=self.handle_back)
        self.back_button.pack(anchor="w", padx=10, pady=(10, 0))

        self.title_label = ctk.CTkLabel(self, text="Homework Statistics", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=(5, 15))

        # --- Filters ---
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(pady=5)

        self.class_menu = ctk.CTkOptionMenu(
            filter_frame, values=["All classes"], command=self.handle_class_change
        )
        self.class_menu.grid(row=0, column=0, padx=5, pady=5)

        self.student_menu = ctk.CTkOptionMenu(filter_frame, values=["All students"])
        self.student_menu.grid(row=0, column=1, padx=5, pady=5)

        self.apply_button = ctk.CTkButton(filter_frame, text="Apply Filters", command=self.refresh_table)
        self.apply_button.grid(row=0, column=2, padx=5, pady=5)

        # --- Table ---
        self.table_box = ctk.CTkScrollableFrame(self, width=420, height=250)
        self.table_box.pack(pady=10)

        self.class_id_lookup = {}    # display name -> id
        self.student_id_lookup = {}  # display name -> id

        self.load_filter_options()
        self.refresh_table()

    def handle_back(self):
        self.on_back()
        self.destroy()

    def load_filter_options(self):
        classes = get_classes_for_school(self.school_id)
        self.class_id_lookup = {c["name"]: c["id"] for c in classes}
        self.class_menu.configure(values=["All classes"] + list(self.class_id_lookup.keys()))
        self.class_menu.set("All classes")

        self.load_students_for_current_class()

    def load_students_for_current_class(self):
        selected_class = self.class_menu.get()
        class_id = self.class_id_lookup.get(selected_class)  # None if "All classes"

        students = get_students_for_school(self.school_id, class_id)
        self.student_id_lookup = {s["username"]: s["id"] for s in students}
        self.student_menu.configure(values=["All students"] + list(self.student_id_lookup.keys()))
        self.student_menu.set("All students")

    def handle_class_change(self, choice):
        self.load_students_for_current_class()

    def refresh_table(self):
        for widget in self.table_box.winfo_children():
            widget.destroy()

        selected_class = self.class_menu.get()
        selected_student = self.student_menu.get()

        class_id = self.class_id_lookup.get(selected_class)
        student_id = self.student_id_lookup.get(selected_student)

        rows = get_performance_rows(self.school_id, class_id, student_id)

        # Header row
        header = ctk.CTkFrame(self.table_box, fg_color="gray20")
        header.pack(fill="x")
        for text, width in [("Student", 100), ("Question", 100), ("Attempts", 70), ("Correct", 70)]:
            ctk.CTkLabel(header, text=text, width=width, font=("Arial", 12, "bold")).pack(side="left", padx=2)

        if not rows:
            ctk.CTkLabel(self.table_box, text="No attempts recorded yet.").pack(pady=10)
            return

        for row_data in rows:
            row = ctk.CTkFrame(self.table_box, fg_color="transparent")
            row.pack(fill="x")
            ctk.CTkLabel(row, text=row_data["username"], width=100).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=row_data["question_text"], width=100).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(row_data["attempts_taken"]), width=70).pack(side="left", padx=2)
            correct_text = "Yes" if row_data["is_correct"] else "No"
            ctk.CTkLabel(row, text=correct_text, width=70).pack(side="left", padx=2)
