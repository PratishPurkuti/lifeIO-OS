import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
service_role_key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

# Anon client for RLS-based client-side or authenticated backend calls
supabase: Client = create_client(url, key)

# Admin client for bypassing RLS (use sparingly)
supabase_admin: Client = None
if service_role_key and not service_role_key.startswith("your_"):
    try:
        supabase_admin = create_client(url, service_role_key)
    except Exception as e:
        print(f"Warning: Could not initialize Supabase Admin client: {e}")

def get_supabase_client():
    return supabase

def get_supabase_admin():
    return supabase_admin
