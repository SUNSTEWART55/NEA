"""
users.py

Data-access functions for the User table.
The UI layer should only ever call these functions -- never
import `supabase` directly.
"""

from app.data.db_client import supabase


def username_exists(username: str) -> bool:
    """Return True if a user with this username already exists."""
    response = (
        supabase.table("User")
        .select("id")
        .eq("username", username)
        .execute()
    )
    return len(response.data) > 0


def create_user(username: str, password: str, email: str, role: str,
                 school_id: int, class_id: int | None = None) -> dict:
    """
    Insert a new user. Raises ValueError if the username is taken.
    class_id is only meaningful for students; leave it None for teachers.
    Returns the created user's row as a dict.
    """
    if username_exists(username):
        raise ValueError(f"Username '{username}' is already taken.")

    response = (
        supabase.table("User")
        .insert({
            "username": username,
            "password": password,
            "email": email,
            "role": role,
            "school_id": school_id,
            "class_id": class_id,
        })
        .execute()
    )
    return response.data[0]


def verify_login(username: str, password: str) -> dict | None:
    """
    Check username + password against the database.
    Returns the user's row as a dict if valid, otherwise None.
    """
    response = (
        supabase.table("User")
        .select("*")
        .eq("username", username)
        .eq("password", password)
        .execute()
    )
    if len(response.data) == 1:
        return response.data[0]
    return None