"""
app/config/supabase.py — AI Career Copilot
Supabase client factory.

Two clients are exposed:
  get_supabase_client()      — service role key, bypasses RLS.
                               Use for all server-side writes where the user_id
                               is explicitly supplied by the calling code.
  get_supabase_anon_client() — anon key, respects RLS.
                               Use for reads scoped to a forwarded user JWT.

Both are thin wrappers; callers get a fresh Client per call.  The Supabase
Python SDK maintains an internal HTTP session so this is cheap.
"""

import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


def get_supabase_client() -> Client:
    """Service role client — bypasses RLS. Use for all backend writes."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise EnvironmentError(
            "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env"
        )
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def get_supabase_anon_client() -> Client:
    """Anon client — respects RLS. Pass a user JWT via set_session() for scoped reads."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise EnvironmentError(
            "Missing SUPABASE_URL or SUPABASE_ANON_KEY in .env"
        )
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
