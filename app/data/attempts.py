"""
attempts.py

Data-access functions for the Attempt table.
"""

from app.data.db_client import supabase


def get_attempt(student_id: int, question_id: int) -> dict | None:
    response = (
        supabase.table("Attempt")
        .select("*")
        .eq("student_id", student_id)
        .eq("question_id", question_id)
        .execute()
    )
    return response.data[0] if response.data else None


def create_attempt(student_id: int, question_id: int) -> dict:
    response = (
        supabase.table("Attempt")
        .insert({
            "student_id": student_id,
            "question_id": question_id,
            "attempts_taken": 0,
            "is_correct": False,
        })
        .execute()
    )
    return response.data[0]


def record_attempt(student_id: int, question_id: int, is_correct: bool) -> dict:
    """
    Get or create the attempt row for this student/question,
    increment attempts_taken, and set is_correct.
    """
    attempt = get_attempt(student_id, question_id)
    if attempt is None:
        attempt = create_attempt(student_id, question_id)

    new_attempts_taken = attempt["attempts_taken"] + 1
    response = (
        supabase.table("Attempt")
        .update({"attempts_taken": new_attempts_taken, "is_correct": is_correct})
        .eq("id", attempt["id"])
        .execute()
    )
    return response.data[0]


def get_attempts_for_student(student_id: int) -> list[dict]:
    response = (
        supabase.table("Attempt")
        .select("*")
        .eq("student_id", student_id)
        .execute()
    )
    return response.data