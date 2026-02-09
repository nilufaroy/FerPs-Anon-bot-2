# SQLite → Supabase Migration Complete ✅

Your FerPs Anonymous Bot has been successfully migrated from **SQLite to Supabase PostgreSQL**.

## What Changed

### Files Modified
- **anon.py** - Updated to use async database functions instead of sqlite3
- **main.py** - Added Supabase initialization in startup
- **requirements.txt** - Added supabase, postgrest-py, pydantic dependencies
- **.env** - Added Supabase credentials (already configured!)

### Files Created
- **database.py** - Supabase database interface (replaces sqlite code)
- **SUPABASE_SCHEMA.sql** - PostgreSQL schema (run in Supabase SQL editor)
- **SUPABASE_SETUP.md** - Complete Supabase setup guide

### Removed
- ❌ SQLite database code (`contextlib.closing`, `sqlite3.Connection`, etc.)
- ❌ Local database file storage (`DB_PATH` setting)
- ❌ SQL schema initialization

---

## Benefits of Supabase

| Feature | SQLite | Supabase |
|---------|--------|----------|
| **Storage** | Local file | Cloud PostgreSQL |
| **Backups** | Manual | Automatic daily |
| **Remote Access** | ❌ No | ✅ Yes (REST API) |
| **Real-time** | ❌ No | ✅ Yes |
| **Scaling** | Limited (file-based) | Unlimited |
| **Security** | Basic | Row-level security |
| **Cost** | Free | Free tier (500MB) |
| **Maintenance** | Manual | Fully managed |

---

## Quick Start

### 1. Create Database Tables

Your credentials are already in `.env`. Just run the schema in Supabase:

1. Go to [supabase.com](https://supabase.com) → **Your Project**
2. Click **SQL Editor** → **New Query**
3. Copy contents of `SUPABASE_SCHEMA.sql`
4. Paste and click **Run**

This creates:
- `settings` table (configuration)
- `moderation` table (submissions)
- `bans` table (banned users)

### 2. Start the Bot

```bash
docker-compose up -d
# or
python main.py
```

✅ Done! Your bot is now using Supabase.

---

## Database Functions

All database operations now use async functions from `database.py`:

```python
# Configuration
await get_setting("CHANNEL_USERNAME")
await set_setting("GROUP_CHAT_ID", "value")

# Records
mod_id = await add_moderation_record(...)
record = await get_moderation_record(mod_id)
await delete_moderation_record(mod_id)

# Bans
is_banned = await is_user_banned(user_id)
await ban_user(user_id, "reason")
await unban_user(user_id)

# Queries
users = await get_all_users()
submissions = await get_user_submissions(user_id=123)
stats = await get_stats()
```

---

## Configuration

Your `.env` already has Supabase credentials:

```env
SUPABASE_URL=https://jjcxskxigeailcbsmxdl.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
POSTGRES_URL=postgres://...
```

**Key Points:**
- `SUPABASE_SERVICE_ROLE_KEY` has full database access (for bot)
- `SUPABASE_ANON_KEY` would be read-only (for frontend)
- Never commit `.env` to git - it has secrets!

---

## Database Schema

### `settings` Table
Stores bot configuration:
```sql
SELECT * FROM settings;
-- Examples:
-- CHANNEL_USERNAME → @ferpsanonymous
-- GROUP_CHAT_ID → 123456789
```

### `moderation` Table
Logs all user submissions:
```sql
SELECT * FROM moderation ORDER BY created_at DESC;
-- Columns: id, user_id, username, first_name, last_name, 
--          message_type, content_text, media_file_id,
--          channel_username, channel_message_id, group_message_id, created_at
```

### `bans` Table
Tracks banned users:
```sql
SELECT * FROM bans;
-- Columns: user_id, reason, banned_at
```

---

## Monitoring Your Database

### In Supabase Dashboard

1. **Table Editor** - View/edit data directly
2. **SQL Editor** - Run custom queries
3. **Backups** - Automatic backups (Settings → Backups)
4. **Database** → **Replication** - Enable real-time

### Common Queries

```sql
-- Total submissions
SELECT COUNT(*) FROM moderation;

-- Unique users
SELECT COUNT(DISTINCT user_id) FROM moderation;

-- Banned users
SELECT COUNT(*) FROM bans;

-- Latest submissions
SELECT created_at, user_id, message_type FROM moderation 
ORDER BY created_at DESC LIMIT 10;

-- User's submissions
SELECT * FROM moderation WHERE user_id = 123456789;

-- Bot settings
SELECT key, value FROM settings;
```

---

## Migration from SQLite

If you had data in the old SQLite database, you can migrate it:

```python
import sqlite3
import asyncio
from database import add_moderation_record, ban_user, set_setting

# Read from old SQLite
old_conn = sqlite3.connect('data/anonymous.db')
old_conn.row_factory = sqlite3.Row

# Migrate settings
cursor = old_conn.execute("SELECT * FROM settings")
for row in cursor.fetchall():
    await set_setting(row['key'], row['value'])

# Migrate moderation records
cursor = old_conn.execute("SELECT * FROM moderation")
for row in cursor.fetchall():
    await add_moderation_record(
        user_id=row['user_id'],
        username=row['username'],
        first_name=row['first_name'],
        last_name=row['last_name'],
        message_type=row['message_type'],
        content_text=row['content_text'],
        media_file_id=row['media_file_id'],
        channel_username=row['channel_username'],
        channel_message_id=row['channel_message_id'],
        group_message_id=row['group_message_id'],
    )

# Migrate bans
cursor = old_conn.execute("SELECT * FROM bans")
for row in cursor.fetchall():
    await ban_user(row['user_id'], row['reason'])

print("✅ Migration complete!")
```

---

## Troubleshooting

### "Connection refused"
```
✅ Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env
✅ Verify Supabase project is active
✅ Test connection: python -c "from database import supabase; print(supabase.health())"
```

### "Table doesn't exist"
```
✅ Run the SQL schema in Supabase SQL Editor
✅ Verify table names: SELECT table_name FROM information_schema.tables;
```

### "Permission denied"
```
✅ Use SERVICE_ROLE_KEY (not ANON_KEY)
✅ Check Row Level Security policies didn't break access
✅ Service role should have full access
```

### "Slow queries"
```
✅ Check indexes exist (schema already creates them)
✅ Monitor from Supabase Dashboard → Performance
✅ If >500MB data, upgrade to paid plan
```

---

## Cost Breakdown

### Supabase Free Tier
- **Database**: 500 MB (enough for 50k+ submissions)
- **Queries**: Unlimited
- **Real-time**: Included
- **Backups**: Daily automatic
- **Storage**: 50 MB file storage (for exports)

### When to Upgrade
- **1 GB+** database → Move to Pro tier ($25/month)
- **High traffic** → Dedicated compute add-on
- **3+ projects** → Pro plan covers 3 projects

For a Telegram bot with thousands of submissions, free tier is plenty!

---

## Security Notes

### Best Practices ✅
1. ✅ `.env` is in `.gitignore` (secrets protected)
2. ✅ Using SERVICE_ROLE_KEY for bot (full permissions)
3. ✅ Row Level Security enabled on all tables
4. ✅ Automatic daily backups enabled
5. ✅ Database is HTTPS-only

### If Key is Leaked
1. Go to Supabase **Project Settings** → **API**
2. Click **Regenerate** on compromised key
3. Update `.env` with new key
4. Restart bot

---

## File Structure

```
.
├── main.py                    ← FastAPI webhook server
├── anon.py                    ← Telegram bot logic (updated)
├── database.py                ← Supabase database interface (NEW)
├── requirements.txt           ← Dependencies (updated)
├── .env                       ← Supabase credentials (updated)
├── SUPABASE_SETUP.md          ← Setup guide (NEW)
├── SUPABASE_SCHEMA.sql        ← Database schema (NEW)
├── docker-compose.yml         ← Docker config
├── DockerFile                 ← Docker image
└── README.md                  ← Main documentation
```

---

## Next Steps

1. ✅ **Run schema**: Copy `SUPABASE_SCHEMA.sql` to Supabase SQL Editor
2. ✅ **Start bot**: `docker-compose up -d`
3. ✅ **Monitor**: Check submissions in Supabase Dashboard
4. ✅ **Backup**: Supabase does this automatically!

## Summary

✅ **Benefits:**
- Cloud database (no local files to manage)
- Automatic backups
- Remote access to data
- Professional PostgreSQL backend
- Scales with your bot
- Free tier very generous

✅ **Changes:**
- Replaced SQLite with Supabase
- Made all DB calls async
- Updated `database.py` with new interface
- Credentials already configured in `.env`

✅ **Testing:**
- All imports working ✓
- Schema ready to deploy ✓
- Bot code compatible ✓
- Ready to run! ✓

Start the bot:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f ferps-anon-bot
```

Access your data:
- Supabase Dashboard: https://app.supabase.com
- SQL Editor for custom queries
- Table Editor for direct data viewing

Happy bot-ing! 🚀
