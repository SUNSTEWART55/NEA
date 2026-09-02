"""
test_connection.py

One-off script to confirm the Supabase connection works.
Run this once, check the output, then delete the test row it creates.
Not part of the actual app.
"""

from app.data.db_client import supabase

# 1. Insert a test teacher into the User table
insert_response = (
    supabase.table("User")
    .insert({
        "username": "test_teacher",
        "password": "temporary_plaintext_password",
        "email": "test_teacher@example.com",
        "role": "teacher",
    })
    .execute()
)

print("Insert response:")
print(insert_response)

# 2. Read all rows back from the User table
select_response = supabase.table("User").select("*").execute()

print("\nAll users currently in the table:")
print(select_response.data)