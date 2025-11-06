import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

_supabase_client: Optional[Client] = None

def init_supabase() -> Client:
    """
    Initialize Supabase client with environment variables.
    This should be called once at application startup.
    """
    global _supabase_client

    try:
        # Use Streamlit secrets (works both locally and in production)
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
    except KeyError:
        # Fallback to environment variables for backward compatibility

        supabase_url = os.getenv("VITE_SUPABASE_URL")
        supabase_key = os.getenv("VITE_SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "1. For Streamlit: Add SUPABASE_URL and SUPABASE_KEY to .streamlit/secrets.toml\n"
                "2. For local development: Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in .env file"
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
