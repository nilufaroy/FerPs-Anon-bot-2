# Supabase Setup Guide

This bot now uses **Supabase PostgreSQL** instead of SQLite for persistent storage.

## What is Supabase?

Supabase is an open-source Firebase alternative with a PostgreSQL database backend. It provides:
- Cloud-hosted PostgreSQL database
- Real-time subscriptions
- RESTful API
- Authentication & security
- Backups and automatic scaling

## Setup Steps

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up
2. Create a new project
3. Set a password (save it somewhere safe)
4. Choose a region
5. Wait for initialization (2-3 minutes)

### 2. Get Your Credentials

After project creation, you'll see:
- **Project URL** - Your Supabase endpoint
- **Anon public key** - For client-side access
- **Service role key** - For bot/server access (more powerful)

Navigate to **Project Settings** → **API** to view keys.

### 3. Run the Database Schema

In Supabase, go to **SQL Editor** and run the contents of `SUPABASE_SCHEMA.sql`:

```bash
# Copy the entire contents of SUPABASE_SCHEMA.sql
# Paste it into Supabase SQL Editor
# Click "Run"
```

This creates the tables:
- `settings` - Configuration (channel, group IDs)
- `moderation` - User submissions
- `bans` - Banned users

### 4. Update `.env`

Your credentials are already in `.env`, but verify they match your Supabase project:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

You can also add other keys (they're provided in the credentials):

```env
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_PUBLISHABLE_KEY=your-publishable-key
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

Or just the Supabase packages:

```bash
pip install supabase postgrest-py httpx
```

### 6. Run the Bot

```bash
docker-compose up -d
# Or locally:
python main.py
```

## Database Tables

### `settings`
Stores configuration:
- `CHANNEL_USERNAME` - Public channel for posts
- `GROUP_CHAT_ID` - Admin group for moderation

### `moderation`
Logs every submission:
- User ID, username, name
- Message content and type (text, photo, video, etc.)
- Channel and group message IDs
- Timestamp

### `bans`
Tracks banned users:
- User ID
- Ban reason
- Ban date

## Key Differences from SQLite

| Aspect | SQLite | Supabase |
|--------|--------|----------|
| Storage | Local file | Cloud database |
| Backups | Manual | Automatic |
| Access | Local only | API/Remote |
| Scaling | Limited | Unlimited |
| Cost | Free | Free tier generous |
| Real-time | No | Yes (subscriptions) |

## Monitoring Your Database

### Via Supabase Dashboard

1. **Table Editor** - View/edit data directly
2. **SQL Editor** - Run custom queries
3. **Database** → **Replication** - Enable real-time
4. **Backups** - View automatic backups

### Via Command Line

```bash
# Connect directly (if using pooler)
psql postgres://user:password@host:port/postgres

# List tables
\dt

# See bot submissions
SELECT user_id, message_type, created_at FROM moderation;

# Check bans
SELECT user_id, reason FROM bans;

# Get settings
SELECT key, value FROM settings;
```

## Backup & Export

### Automatic Backups

Supabase automatically backs up your database daily. View in **Project Settings** → **Backups**.

### Manual Export

```bash
# Export as SQL
pg_dump postgres://user:pass@host/postgres > backup.sql

# Export as CSV
SELECT * FROM moderation
TO PROGRAM 'cat > /tmp/submissions.csv' 
WITH (FORMAT csv, HEADER);
```

## Common Tasks

### Check Bot Settings

```sql
SELECT * FROM settings;
```

### See All Submissions

```sql
SELECT created_at, user_id, message_type, content_text 
FROM moderation 
ORDER BY created_at DESC 
LIMIT 20;
```

### Check Banned Users

```sql
SELECT * FROM bans;
```

### Get User's Submissions

```sql
SELECT * FROM moderation 
WHERE user_id = 123456789 
ORDER BY created_at DESC;
```

### Unban User (from SQL)

```sql
DELETE FROM bans WHERE user_id = 123456789;
```

### Count Statistics

```sql
SELECT 
  (SELECT COUNT(*) FROM moderation) as total_posts,
  (SELECT COUNT(*) FROM bans) as banned_users,
  (SELECT COUNT(DISTINCT user_id) FROM moderation) as unique_users;
```

## Troubleshooting

### "Can't connect to Supabase"
- Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are correct
- Ensure they're in .env without quotes
- Test: `python -c "from database import supabase; print('OK')"`

### "Table doesn't exist"
- Run the SQL schema again in Supabase SQL Editor
- Check table names match exactly

### Slow queries
- Add indexes (already done by schema)
- Check data volume: `SELECT COUNT(*) FROM moderation;`
- Monitor with Supabase dashboard

### "Permission denied"
- Use SERVICE_ROLE_KEY, not ANON_KEY
- Service role has full permissions for bot operations
- Anon key is  read-only by default

## Migrate from SQLite

If you had an earlier version with SQLite:

```python
import sqlite3
import json
from supabase import create_client

# Read from SQLite
conn = sqlite3.connect('data/anonymous.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Migrate to Supabase
supabase = create_client(url, key)

# Copy settings
cursor.execute("SELECT * FROM settings")
for row in cursor.fetchall():
    supabase.table("settings").insert({
        "key": row["key"],
        "value": row["value"]
    }).execute()

# Copy moderation records
# Similar process for other tables
```

## Free Tier Limits

Supabase free tier includes:
- ✅ Unlimited queries
- ✅ 500 MB database size
- ✅ Real-time subscriptions
- ✅ 50 MB file storage
- ✅ Email auth

For larger deployments, upgrade to a paid plan.

## Security

### Best Practices

1. **Never commit `.env` to git** - Use `.gitignore` ✓
2. **Use SERVICE_ROLE_KEY for bot** - Has full access ✓
3. **Use ANON_KEY for frontend** - Limited read-only ✓
4. **Enable RLS (Row Level Security)** - Already configured ✓
5. **Rotate keys if leaked** - Regenerate in dashboard

### Row Level Security (RLS)

The schema enables RLS with policies:
- Service role: Full access (for bot)
- Anon role: Read-only (for frontend, if added)

You can add more policies in **Auth** → **Policies**.

## Next Steps

1. ✅ Create Supabase project
2. ✅ Run SQL schema
3. ✅ Add credentials to `.env`
4. ✅ Run bot: `docker-compose up -d`
5. 📊 Monitor submissions in Supabase dashboard
6. 🔄 Scale up if needed (plan upgrade takes 2 minutes)

## Support

- Supabase docs: https://supabase.com/docs
- PostgreSQL docs: https://www.postgresql.org/docs/
- python-postgrest: https://github.com/supabase-community/postgrest-py
