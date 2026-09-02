"""
student_stats_view.py

Shows a student's own performance across all their attempted questions.
"""

import customtkinter as ctk
from app.data.statistics import get_performance_rows


class StudentStatsView(ctk.CTkFrame):
    def __init__(self, master, user: dict, on_back):
        super().__init__(master)
        self.user = user
        self.on_back = on_back

        ctk.CTkButton(self, text="< Back", width=80, command=self.handle_back).pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkLabel(self, text="My Stats", font=("Arial", 20, "bold")).pack(pady=(5, 15))

        self.table_box = ctk.CTkScrollableFrame(self, width=380, height=280)
        self.table_box.pack(pady=5)

        self.refresh_table()

    def handle_back(self):
        self.on_back()
        self.destroy()

    def refresh_table(self):
        for widget in self.table_box.winfo_children():
            widget.destroy()

        rows = get_performance_rows(self.user["school_id"], student_id=self.user["id"])

        header = ctk.CTkFrame(self.table_box, fg_color="gray20")
        header.pack(fill="x")
        for text, width in [("Question", 150), ("Attempts", 90), ("Correct", 90)]:
            ctk.CTkLabel(header, text=text, width=width, font=("Arial", 12, "bold")).pack(side="left", padx=2)

        if not rows:
            ctk.CTkLabel(self.table_box, text="You haven't attempted any homework yet.").pack(pady=10)
            return

        for row_data in rows:
            row = ctk.CTkFrame(self.table_box, fg_color="transparent")
            row.pack(fill="x")
            ctk.CTkLabel(row, text=row_data["question_text"], width=150).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(row_data["attempts_taken"]), width=90).pack(side="left", padx=2)
            ctk.CTkLabel(row, text="Yes" if row_data["is_correct"] else "No", width=90).pack(side="left", padx=2)