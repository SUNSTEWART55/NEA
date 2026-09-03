"""
leaderboard_view.py

Ranked leaderboard of students in the logged-in student's own class,
ranked by number of correctly answered questions.
"""

import customtkinter as ctk
from app.data.statistics import get_leaderboard


class LeaderboardView(ctk.CTkFrame):
    def __init__(self, master, user: dict, on_back):
        super().__init__(master)
        self.user = user
        self.on_back = on_back

        ctk.CTkButton(self, text="< Back", width=80, command=self.handle_back).pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkLabel(self, text="Class Leaderboard", font=("Arial", 20, "bold")).pack(pady=(5, 15))

        self.table_box = ctk.CTkScrollableFrame(self, width=320, height=280)
        self.table_box.pack(pady=5)

        self.refresh_table()

    def handle_back(self):
        self.on_back()
        self.destroy()

    def refresh_table(self):
        for widget in self.table_box.winfo_children():
            widget.destroy()

        if not self.user.get("class_id"):
            ctk.CTkLabel(self.table_box, text="You're not assigned to a class yet.").pack(pady=10)
            return

        leaderboard = get_leaderboard(self.user["class_id"])

        header = ctk.CTkFrame(self.table_box, fg_color="gray20")
        header.pack(fill="x")
        for text, width in [("Rank", 50), ("Student", 150), ("Correct", 90)]:
            ctk.CTkLabel(header, text=text, width=width, font=("Arial", 12, "bold")).pack(side="left", padx=2)

        if not leaderboard:
            ctk.CTkLabel(self.table_box, text="No students found in your class.").pack(pady=10)
            return

        for i, row_data in enumerate(leaderboard, start=1):
            row = ctk.CTkFrame(self.table_box, fg_color="transparent")
            row.pack(fill="x")
            highlight = row_data["username"] == self.user["username"]
            color = "yellow" if highlight else "white"
            ctk.CTkLabel(row, text=str(i), width=50, text_color=color).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=row_data["username"], width=150, text_color=color).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(row_data["correct_count"]), width=90, text_color=color).pack(side="left", padx=2)