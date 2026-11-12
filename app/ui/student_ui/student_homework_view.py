"""
student_homework_view.py

Lists available questions and lets the student upload a photo of
their written answer to be marked.

NOTE: marking is currently stubbed (see app/services/marking.py) --
it returns a random result until the real ML pipeline is wired in.
"""

import customtkinter as ctk
from tkinter import filedialog
from app.data.questions import get_available_questions_for_student
from app.data.attempts import record_attempt
from app.services.marking import mark_answer


class StudentHomeworkView(ctk.CTkFrame):
    def __init__(self, master, user: dict, on_back):
        super().__init__(master)
        self.user = user
        self.on_back = on_back

        ctk.CTkButton(self, text="< Back", width=80, command=self.handle_back).pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkLabel(self, text="Homework", font=("Arial", 20, "bold")).pack(pady=(5, 10))
        ctk.CTkLabel(
            self, text="Marking is still a work in progress -- results are simulated for now.",
            text_color="gray", wraplength=350
        ).pack(pady=(0, 10))

        self.feedback_label = ctk.CTkLabel(self, text="", font=("Arial", 14, "bold"))
        self.feedback_label.pack(pady=(0, 10))

        self.questions_box = ctk.CTkScrollableFrame(self, width=380, height=250)
        self.questions_box.pack(pady=5)

        self.refresh_questions_list()

    def handle_back(self):
        self.on_back()
        self.destroy()

    def refresh_questions_list(self):
        for widget in self.questions_box.winfo_children():
            widget.destroy()

        questions = get_available_questions_for_student(self.user)
        symbols = {"add": "+", "sub": "-", "mul": "x", "div": "/"}

        if not questions:
            ctk.CTkLabel(self.questions_box, text="No homework outstanding right now.").pack(pady=10)
            return

        for q in questions:
            row = ctk.CTkFrame(self.questions_box, fg_color="transparent")
            row.pack(fill="x", pady=4)

            symbol = symbols.get(q["operation"], "?")
            ctk.CTkLabel(row, text=f"{q['operand_a']} {symbol} {q['operand_b']} = ?", anchor="w", width=150).pack(side="left", padx=5)

            ctk.CTkButton(
                row, text="Upload Answer", width=120,
                command=lambda question=q: self.handle_upload(question)
            ).pack(side="right", padx=5)

    def handle_upload(self, question: dict):
        file_path = filedialog.askopenfilename(
            title="Select a photo of your answer",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        if not file_path:
            return  # cancelled

        is_correct = mark_answer(question["answer"], file_path)
        record_attempt(self.user["id"], question["id"], is_correct)

        if is_correct:
            self.feedback_label.configure(text="Correct! Well done.", text_color="lightgreen")
        else:
            self.feedback_label.configure(text="Not quite right -- try again.", text_color="orange")

        self.refresh_questions_list()