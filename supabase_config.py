"""Supabase configuration and client initialization"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_BUCKET_NAME = os.getenv('SUPABASE_BUCKET_NAME', 'loan-documents')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Initialize Supabase client
supabase: Client = None
admin_supabase: Client = None

def init_supabase():
    """Initialize Supabase client"""
    global supabase
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase credentials not found. "
            "Please set SUPABASE_URL and SUPABASE_KEY in .env file"
        )
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized successfully")
    return supabase

def get_supabase_client():
    """Get Supabase client instance"""
    global supabase
    if supabase is None:
        supabase = init_supabase()
    return supabase

def get_supabase_admin_client():
    """Get Supabase admin client instance using service role key when available"""
    global admin_supabase
    if admin_supabase is not None:
        return admin_supabase
    if SUPABASE_SERVICE_ROLE_KEY and SUPABASE_URL:
        admin_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("✅ Supabase admin client initialized successfully")
        return admin_supabase
    # Fallback to regular client if service role key is not set
    # WARNING: falling back to the regular client (anon/public key). This
    # client may not have permission to perform storage admin actions such
    # as uploading to private buckets or creating buckets. If uploads fail,
    # set SUPABASE_SERVICE_ROLE_KEY in your .env with a service_role key.
    print("⚠️  SUPABASE_SERVICE_ROLE_KEY not set — using regular client (limited permissions)")
    return get_supabase_client()
