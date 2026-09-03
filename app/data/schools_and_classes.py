"""
schools_and_classes.py

Data-access functions for School and Class, plus helpers used to
populate the statistics filter dropdowns.
"""

from app.data.db_client import supabase


def get_or_create_school(name: str) -> dict:
    name = name.strip()
    response = supabase.table("School").select("*").eq("name", name).execute()
    if response.data:
        return response.data[0]

    insert_response = supabase.table("School").insert({"name": name}).execute()
    return insert_response.data[0]


def get_or_create_class(school_id: int, name: str) -> dict:
    name = name.strip()
    response = (
        supabase.table("Class")
        .select("*")
        .eq("school_id", school_id)
        .eq("name", name)
        .execute()
    )
    if response.data:
        return response.data[0]

    insert_response = (
        supabase.table("Class")
        .insert({"school_id": school_id, "name": name})
        .execute()
    )
    return insert_response.data[0]


def get_classes_for_school(school_id: int) -> list[dict]:
    response = (
        supabase.table("Class")
        .select("*")
        .eq("school_id", school_id)
        .order("name")
        .execute()
    )
    return response.data


def get_students_for_school(school_id: int, class_id: int = None) -> list[dict]:
    query = (
        supabase.table("User")
        .select("*")
        .eq("school_id", school_id)
        .eq("role", "student")
    )
    if class_id is not None:
        query = query.eq("class_id", class_id)
    response = query.order("username").execute()
    return response.data