import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase_client: Optional[Client] = None

def init_supabase() -> Client:
    """
    Initialize Supabase client with environment variables.
    This should be called once at application startup.
    """
    global _supabase_client

    supabase_url = os.getenv("VITE_SUPABASE_URL")
    supabase_key = os.getenv("VITE_SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Missing Supabase credentials. Please ensure VITE_SUPABASE_URL and "
            "VITE_SUPABASE_ANON_KEY are set in your .env file."
        )

    _supabase_client = create_client(supabase_url, supabase_key)
    return _supabase_client

def get_supabase_client() -> Client:
    """
    Get the initialized Supabase client.
    Creates a new client if one doesn't exist.
    """
    global _supabase_client

    if _supabase_client is None:
        _supabase_client = init_supabase()

    return _supabase_client
