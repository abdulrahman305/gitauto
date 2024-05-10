import os
from services.supabase import SupabaseManager
from config import (
    OWNER_ID,
    USER_ID,
    USER_NAME,
    INSTALLATION_ID,
)

SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")


def wipe_installation_owner_user_data() -> None:
    """Wipe all data from installations, owners, and users tables"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)
    supabase_manager.client.table("usage").delete().eq("user_id", USER_ID).eq(
        "installation_id", INSTALLATION_ID
    ).execute()

    supabase_manager.client.table("user_installations").delete().eq(
        "user_id", USER_ID
    ).eq("installation_id", INSTALLATION_ID).execute()

    supabase_manager.client.table("users").delete().eq("user_id", USER_ID).eq(
        "user_id", USER_ID
    ).execute()

    supabase_manager.client.table("issues").delete().eq(
        "installation_id", INSTALLATION_ID
    ).execute()

    supabase_manager.client.table("installations").delete().eq(
        "installation_id", INSTALLATION_ID
    ).execute()
    supabase_manager.client.table("owners").delete().eq("owner_id", OWNER_ID).execute()
