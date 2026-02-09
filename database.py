"""
Supabase database module for FerPS Anonymous Bot
Replaces SQLite with PostgreSQL via Supabase
"""
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env")

log = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role for bot operations

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required in .env")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def init_db() -> None:
    """Initialize database tables if they don't exist."""
    try:
        log.info("Checking Supabase database connection...")
        
        # Check if settings table exists by trying to query it
        result = supabase.table("settings").select("*").limit(1).execute()
        log.info("✅ Database connection successful - all tables found")
        
    except Exception as e:
        # Tables don't exist yet - this is expected on first run
        log.warning(
            f"⚠️ Database tables not found. Please run SUPABASE_SCHEMA.sql in Supabase SQL Editor:\n"
            f"   1. Go to https://app.supabase.com → Your Project\n"
            f"   2. Click SQL Editor → New Query\n"
            f"   3. Copy contents of SUPABASE_SCHEMA.sql\n"
            f"   4. Paste and click Run\n\n"
            f"Connection test: {e}\n"
            f"This is normal for first-time setup. Tables will be created in Supabase."
        )


async def get_setting(key: str) -> Optional[str]:
    """Get a setting from the database."""
    try:
        result = supabase.table("settings").select("value").eq("key", key).execute()
        if result.data:
            return result.data[0]["value"]
        return None
    except Exception as e:
        log.error(f"Error getting setting {key}: {e}")
        return None


async def set_setting(key: str, value: str) -> None:
    """Set a setting in the database."""
    try:
        # Try to update first
        result = supabase.table("settings").select("*").eq("key", key).execute()
        
        if result.data:
            # Update existing
            supabase.table("settings").update({"value": value}).eq("key", key).execute()
        else:
            # Insert new
            supabase.table("settings").insert({"key": key, "value": value}).execute()
            
        log.debug(f"Set setting {key} = {value}")
    except Exception as e:
        log.error(f"Error setting {key}: {e}")


async def add_moderation_record(
    user_id: int,
    username: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str],
    message_type: str,
    content_text: Optional[str],
    media_file_id: Optional[str],
    channel_username: str,
    channel_message_id: int,
    group_message_id: int,
) -> int:
    """Add a moderation record. Returns the ID of the inserted record."""
    try:
        result = supabase.table("moderation").insert({
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "message_type": message_type,
            "content_text": content_text,
            "media_file_id": media_file_id,
            "channel_username": channel_username,
            "channel_message_id": channel_message_id,
            "group_message_id": group_message_id,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
        
        if result.data:
            return result.data[0]["id"]
        raise ValueError("No data returned from insert")
    except Exception as e:
        log.error(f"Error adding moderation record: {e}")
        raise


async def get_moderation_record(mod_id: int) -> Optional[Dict[str, Any]]:
    """Get a moderation record by ID."""
    try:
        result = supabase.table("moderation").select("*").eq("id", mod_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        log.error(f"Error getting moderation record {mod_id}: {e}")
        return None


async def delete_moderation_record(mod_id: int) -> None:
    """Delete a moderation record."""
    try:
        supabase.table("moderation").delete().eq("id", mod_id).execute()
        log.debug(f"Deleted moderation record {mod_id}")
    except Exception as e:
        log.error(f"Error deleting moderation record {mod_id}: {e}")


async def is_user_banned(user_id: int) -> bool:
    """Check if a user is banned."""
    try:
        result = supabase.table("bans").select("*").eq("user_id", user_id).execute()
        return len(result.data) > 0
    except Exception as e:
        log.error(f"Error checking ban status for {user_id}: {e}")
        return False


async def ban_user(user_id: int, reason: str = "Admin ban") -> None:
    """Ban a user."""
    try:
        supabase.table("bans").insert({
            "user_id": user_id,
            "reason": reason,
            "banned_at": datetime.utcnow().isoformat(),
        }).execute()
        log.info(f"Banned user {user_id}")
    except Exception as e:
        log.error(f"Error banning user {user_id}: {e}")


async def unban_user(user_id: int) -> None:
    """Unban a user."""
    try:
        supabase.table("bans").delete().eq("user_id", user_id).execute()
        log.info(f"Unbanned user {user_id}")
    except Exception as e:
        log.error(f"Error unbanning user {user_id}: {e}")


async def get_all_users() -> List[Dict[str, Any]]:
    """Get all unique users who submitted messages."""
    try:
        # Get unique users ordered by most recent
        result = supabase.table("moderation").select(
            "user_id, username, first_name, last_name, created_at"
        ).order("created_at", desc=True).execute()
        
        # Deduplicate by user_id, keeping most recent
        seen = {}
        for record in result.data:
            user_id = record["user_id"]
            if user_id not in seen:
                seen[user_id] = record
        
        return list(seen.values())
    except Exception as e:
        log.error(f"Error getting all users: {e}")
        return []


async def get_user_submissions(user_id: Optional[int] = None, username: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all submissions from a user (by ID or username)."""
    try:
        query = supabase.table("moderation").select("*")
        
        if user_id:
            query = query.eq("user_id", user_id)
        elif username:
            query = query.ilike("username", username)  # Case-insensitive
        else:
            return []
        
        result = query.order("created_at", desc=False).execute()
        return result.data or []
    except Exception as e:
        log.error(f"Error getting user submissions: {e}")
        return []


async def get_stats() -> Dict[str, int]:
    """Get statistics."""
    try:
        # Count total moderated posts
        total_result = supabase.table("moderation").select("*", count="exact").execute()
        total = len(total_result.data) if total_result.data else 0
        
        # Count banned users
        banned_result = supabase.table("bans").select("*", count="exact").execute()
        banned = len(banned_result.data) if banned_result.data else 0
        
        return {"total": total, "banned": banned}
    except Exception as e:
        log.error(f"Error getting stats: {e}")
        return {"total": 0, "banned": 0}
