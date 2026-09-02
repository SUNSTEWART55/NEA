"""
db_client.py

Single place that creates and holds the Supabase client.
Every other file in the data layer (and nowhere else) should import
`supabase` from here rather than creating its own client.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load variables from .env into the environment
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Missing SUPABASE_URL or SUPABASE_KEY. "
        "Check that your .env file exists in the project root."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)