"""
statistics.py

Builds the combined student-performance rows for the teacher
statistics screen. Joins Attempt, User, and Question data client-side
(kept simple and explicit rather than relying on PostgREST embedding
syntax, which is easy to get wrong when new to Supabase).
"""

from app.data.db_client import supabase
from app.data.schools_and_classes import get_students_for_school


def get_performance_rows(school_id: int, class_id: int = None, student_id: int = None) -> list[dict]:
    # 1. Work out which students are in scope
    if student_id is not None:
        student_ids = [student_id]
    else:
        students = get_students_for_school(school_id, class_id)
        student_ids = [s["id"] for s in students]

    if not student_ids:
        return []

    # 2. Fetch attempts for those students
    attempts_response = (
        supabase.table("Attempt")
        .select("*")
        .in_("student_id", student_ids)
        .execute()
    )
    attempts = attempts_response.data
    if not attempts:
        return []

    # 3. Fetch the related users and questions in bulk
    question_ids = list({a["question_id"] for a in attempts})

    users_response = supabase.table("User").select("*").in_("id", student_ids).execute()
    questions_response = supabase.table("Question").select("*").in_("id", question_ids).execute()

    users_by_id = {u["id"]: u for u in users_response.data}
    questions_by_id = {q["id"]: q for q in questions_response.data}

    symbols = {"add": "+", "sub": "-", "mul": "x", "div": "/"}

    # 4. Combine into display-ready rows
    rows = []
    for a in attempts:
        user = users_by_id.get(a["student_id"])
        question = questions_by_id.get(a["question_id"])
        if not user or not question:
            continue

        symbol = symbols.get(question["operation"], "?")
        rows.append({
            "username": user["username"],
            "question_text": f"{question['operand_a']} {symbol} {question['operand_b']}",
            "answer": question["answer"],
            "attempts_taken": a["attempts_taken"],
            "is_correct": a["is_correct"],
        })

    return rows

def get_leaderboard(class_id: int) -> list[dict]:
    """
    Ranks students in a class by number of questions answered correctly.
    """
    students_response = (
        supabase.table("User")
        .select("*")
        .eq("class_id", class_id)
        .eq("role", "student")
        .execute()
    )
    students = students_response.data
    if not students:
        return []

    student_ids = [s["id"] for s in students]
    attempts_response = (
        supabase.table("Attempt")
        .select("*")
        .in_("student_id", student_ids)
        .eq("is_correct", True)
        .execute()
    )
    attempts = attempts_response.data

    correct_counts = {s["id"]: 0 for s in students}
    for a in attempts:
        correct_counts[a["student_id"]] = correct_counts.get(a["student_id"], 0) + 1

    leaderboard = [
        {"username": s["username"], "correct_count": correct_counts.get(s["id"], 0)}
        for s in students
    ]
    leaderboard.sort(key=lambda row: row["correct_count"], reverse=True)
    return leaderboard