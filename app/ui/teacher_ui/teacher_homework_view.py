"""
teacher_homework_view.py

Homework section: set a new question, view and delete existing questions.
"""

import customtkinter as ctk
from app.data.questions import create_question, get_questions_for_teacher, delete_question


class TeacherHomeworkView(ctk.CTkFrame):
    def __init__(self, master, user: dict, on_back):
        super().__init__(master)
        self.user = user
        self.on_back = on_back

        self.back_button = ctk.CTkButton(self, text="< Back", width=80, command=self.handle_back)
        self.back_button.pack(anchor="w", padx=10, pady=(10, 0))

        self.title_label = ctk.CTkLabel(self, text="Homework", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=(5, 15))

        # --- Question creation form ---
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(pady=5)

        self.operation_menu = ctk.CTkOptionMenu(form_frame, values=["add", "sub", "mul", "div"])
        self.operation_menu.set("add")
        self.operation_menu.grid(row=0, column=0, columnspan=2, pady=5)

        self.operand_a_entry = ctk.CTkEntry(form_frame, placeholder_text="First number", width=140)
        self.operand_a_entry.grid(row=1, column=0, padx=5, pady=5)

        self.operand_b_entry = ctk.CTkEntry(form_frame, placeholder_text="Second number", width=140)
        self.operand_b_entry.grid(row=1, column=1, padx=5, pady=5)

        self.max_attempts_entry = ctk.CTkEntry(form_frame, placeholder_text="Max attempts (default 3)", width=290)
        self.max_attempts_entry.grid(row=2, column=0, columnspan=2, pady=5)

        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack(pady=(5, 0))

        self.add_button = ctk.CTkButton(self, text="Add Question", command=self.handle_add_question)
        self.add_button.pack(pady=15)

        # --- List of existing questions ---
        self.questions_label = ctk.CTkLabel(self, text="Your questions:", font=("Arial", 14, "bold"))
        self.questions_label.pack(pady=(10, 5))

        self.questions_box = ctk.CTkScrollableFrame(self, width=360, height=180)
        self.questions_box.pack(pady=5)

        self.refresh_questions_list()

    def handle_back(self):
        self.on_back()
        self.destroy()

    def handle_add_question(self):
        self.error_label.configure(text="")

        operation = self.operation_menu.get()
        operand_a_text = self.operand_a_entry.get().strip()
        operand_b_text = self.operand_b_entry.get().strip()
        max_attempts_text = self.max_attempts_entry.get().strip()

        if not operand_a_text.isdigit() or not operand_b_text.isdigit():
            self.error_label.configure(text="Both numbers must be whole numbers.")
            return

        operand_a = int(operand_a_text)
        operand_b = int(operand_b_text)
        max_attempts = int(max_attempts_text) if max_attempts_text.isdigit() else 3

        if operation == "div" and operand_b == 0:
            self.error_label.configure(text="Cannot divide by zero.")
            return

        create_question(
            teacher_id=self.user["id"],
            operation=operation,
            operand_a=operand_a,
            operand_b=operand_b,
            max_attempts=max_attempts,
        )

        self.operand_a_entry.delete(0, "end")
        self.operand_b_entry.delete(0, "end")
        self.max_attempts_entry.delete(0, "end")
        self.refresh_questions_list()

    def handle_delete_question(self, question_id: int):
        delete_question(question_id)
        self.refresh_questions_list()

    def refresh_questions_list(self):
        for widget in self.questions_box.winfo_children():
            widget.destroy()

        questions = get_questions_for_teacher(self.user["id"])
        symbols = {"add": "+", "sub": "-", "mul": "x", "div": "/"}

        if not questions:
            ctk.CTkLabel(self.questions_box, text="No questions set yet.").pack(pady=5)
            return

        for q in questions:
            row = ctk.CTkFrame(self.questions_box, fg_color="transparent")
            row.pack(fill="x", pady=2)

            symbol = symbols.get(q["operation"], "?")
            text = f"{q['operand_a']} {symbol} {q['operand_b']} = {q['answer']}  (max {q['max_attempts']})"
            ctk.CTkLabel(row, text=text, anchor="w").pack(side="left", fill="x", expand=True, padx=5)

            delete_btn = ctk.CTkButton(
                row, text="Delete", width=60, fg_color="darkred", hover_color="red",
                command=lambda qid=q["id"]: self.handle_delete_question(qid)
            )
            delete_btn.pack(side="right", padx=5)