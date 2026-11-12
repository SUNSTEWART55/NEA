"""
users.py
 
Data-access functions for the User table.
The UI layer should only ever call these functions -- never
import `supabase` directly.
"""
 
import re
 
from app.data.db_client import supabase
 
PASSWORD_REQUIREMENTS_TEXT = (
    "Password must be at least 8 characters and include\n"
    "one capital letter and one special character."
)
 
_SPECIAL_CHAR_PATTERN = re.compile(r"[!@#$%^&*(),.?\":{}|<>_\-+=~`\[\];'/\\]")
 
 
def is_valid_password(password: str) -> bool:
    """Check password against the app's minimum security requirements."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not _SPECIAL_CHAR_PATTERN.search(password):
        return False
    return True
 
 
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
 
 
def update_user(user_id: int, **fields) -> dict:
    """
    Update one or more fields on an existing user (e.g. email, password,
    username). Pass only the fields you want to change as keyword
    arguments. Raises ValueError if changing to a username that's
    already taken by a different user.
    """
    if not fields:
        raise ValueError("No fields given to update.")
 
    if "username" in fields and fields["username"]:
        existing = (
            supabase.table("User")
            .select("id")
            .eq("username", fields["username"])
            .neq("id", user_id)
            .execute()
        )
        if existing.data:
            raise ValueError(f"Username '{fields['username']}' is already taken.")
 
    response = (
        supabase.table("User")
        .update(fields)
        .eq("id", user_id)
        .execute()
    )
    return response.data[0]
 
 
def delete_user(user_id: int) -> None:
    """Permanently delete a user's account and its row from the User table."""
    supabase.table("User").delete().eq("id", user_id).execute()
