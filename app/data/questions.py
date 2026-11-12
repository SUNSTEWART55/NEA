"""
questions.py

Data-access functions for the Question table.
"""

from app.data.db_client import supabase


def create_question(teacher_id: int, operation: str, operand_a: int,
                     operand_b: int, max_attempts: int = 3) -> dict:
    """
    Insert a new question, computing the correct answer from the operands.
    Returns the created question's row as a dict.
    """
    answer = compute_answer(operation, operand_a, operand_b)

    response = (
        supabase.table("Question")
        .insert({
            "teacher_id": teacher_id,
            "operation": operation,
            "operand_a": operand_a,
            "operand_b": operand_b,
            "answer": answer,
            "max_attempts": max_attempts,
        })
        .execute()
    )
    return response.data[0]

def delete_question(question_id: int) -> None:
    """
    Delete a question. Attempts referencing it are deleted first
    since there's no database-level cascade configured.
    """
    supabase.table("Attempt").delete().eq("question_id", question_id).execute()
    supabase.table("Question").delete().eq("id", question_id).execute()

def compute_answer(operation: str, operand_a: int, operand_b: int) -> int:
    if operation == "add":
        return operand_a + operand_b
    elif operation == "sub":
        return operand_a - operand_b
    elif operation == "mul":
        return operand_a * operand_b
    elif operation == "div":
        return operand_a // operand_b
    else:
        raise ValueError(f"Unknown operation: {operation}")


def get_questions_for_teacher(teacher_id: int) -> list[dict]:
    """Return all questions set by a given teacher, most recent first."""
    response = (
        supabase.table("Question")
        .select("*")
        .eq("teacher_id", teacher_id)
        .order("id", desc=True)
        .execute()
    )
    return response.data

def get_available_questions_for_student(student: dict) -> list[dict]:
    """
    Questions set by any teacher in the student's school, excluding
    ones already answered correctly or where max_attempts is used up.
    """
    from app.data.attempts import get_attempts_for_student

    teachers_response = (
        supabase.table("User")
        .select("id")
        .eq("school_id", student["school_id"])
        .eq("role", "teacher")
        .execute()
    )
    teacher_ids = [t["id"] for t in teachers_response.data]
    if not teacher_ids:
        return []

    questions_response = (
        supabase.table("Question")
        .select("*")
        .in_("teacher_id", teacher_ids)
        .order("id", desc=True)
        .execute()
    )
    all_questions = questions_response.data

    attempts = get_attempts_for_student(student["id"])
    attempts_by_question = {a["question_id"]: a for a in attempts}

    available = []
    for q in all_questions:
        attempt = attempts_by_question.get(q["id"])
        if attempt is None:
            available.append(q)
        elif not attempt["is_correct"] and attempt["attempts_taken"] < q["max_attempts"]:
            available.append(q)
    return available