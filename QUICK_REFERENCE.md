# Quick Reference Guide

## Installation & Setup

```bash
# 1. Copy and configure
cp .env.example .env
# Edit .env with BOT_TOKEN, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, BASE_URL

# Or use interactive setup
python setup.py

# 2. Run with Docker Compose
docker-compose up -d

# 3. Check if running
curl http://localhost:8080/health
```

## Running Mode (Webhook)

```bash
# In .env:
BASE_URL=https://yourdomain.com
PORT=8080

# With Docker:
docker-compose up -d

# Local testing with ngrok:
bash webhook-dev.sh
```

## First Time Setup

1. **Get Bot Token**
   - Chat with [@BotFather](https://t.me/BotFather)
   - Run `/start` → `/newbot` → follow prompts
   - Copy your token

2. **Get Your User ID**
   - Chat with [@userinfobot](https://t.me/userinfobot)
   - Copy your user ID

3. **Configure Bot**
   - Edit `.env` with your token and user ID
   - Run `python setup.py` for interactive setup

4. **Create Telegram Groups/Channels**
   - Create a private **admin group** (just for mods)
   - Create a public **channel** for anonymous posts
   - Add the bot to both

5. **Register Groups with Bot**
   - In admin group: run `/setgroup`
   - In admin group: run `/setchannel @channel_name`
   - Bot confirms with ✅

6. **Test**
   - DM the bot a test message
   - Should appear in channel + admin group

## Docker Commands

```bash
# Start bot
docker-compose up -d

# Stop bot
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Remove everything (careful!)
docker-compose down -v
```

## Admin Commands

| Command | Usage | Effect |
|---------|-------|--------|
| `/setgroup` | Run in admin group | Register group for moderation |
| `/setchannel` | `/setchannel @channel` | Set public channel |
| `/user` | Run in admin group | List all senders |
| `/info` | `/info @user` or `/info 123` | Export user data as Excel |
| `/stats` | Run in admin group | Show stats |
| `/start` | DM bot | Get welcome message |

## Moderation (Admin Group)

**Message Buttons:**
- 🗑 **Delete** - Remove from channel only
- 🚫 **Ban** - Remove + ban user
- 👤 **Profile** - Open user's Telegram profile
- 🔗 **View** - Jump to channel post

## Webhook Debugging

```bash
# Check webhook status
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo" | jq

# Expected: "pending_update_count": 0

# Test webhook endpoint
curl -X POST http://localhost:8080/webhook/telegram \
  -H "Content-Type: application/json" \
  -d '{"update_id": 0}'

# View logs
docker-compose logs ferps-anon-bot
```

## Database Backup

```sql
SELECT COUNT(*) FROM moderation;
SELECT user_id, COUNT(*) FROM moderation GROUP BY user_id;
```

Run in the Supabase SQL Editor.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot not receiving messages | Check webhook with `getWebhookInfo`, verify BASE_URL is HTTPS |
| "Can't post to channel" | Make bot admin in channel, use `@channel` not channel ID |
| "Database tables not found" | Run `SUPABASE_SCHEMA.sql` and verify Supabase env vars |
| 502 Bad Gateway (nginx) | Check if container is running: `docker ps` |

## Environment Variables

```
BOT_TOKEN                 Required - Telegram bot token
SUPABASE_URL              Required - Supabase project URL
SUPABASE_SERVICE_ROLE_KEY Required - Supabase service role key
BASE_URL                 Webhook URL (required for webhook mode)
PORT                     Listen port (default 8080)
DEFAULT_CHANNEL          Default channel for posts (@name)
ADMIN_IDS                Comma-separated admin user IDs
TZ                       Timezone (default UTC)
```

## File Structure

```
.
├── main.py              ← FastAPI webhook server
├── anon.py              ← Telegram bot logic
├── requirements.txt     ← Python dependencies
├── DockerFile           ← Docker image definition
├── docker-compose.yml   ← Docker compose config
├── .env                 ← Your config (secret!)
├── .env.example         ← Config template
├── setup.py             ← Interactive setup wizard
├── webhook-dev.sh       ← ngrok test helper
├── README.md            ← Full documentation
├── WEBHOOK_SETUP.md     ← Webhook deployment guide
└── QUICK_REFERENCE.md   ← This file
```

## Common Tasks

### Change admin group
```bash
# 1. Add bot to new group
# 2. In new group, run: /setgroup
```

### Change channel
```bash
# 1. Add bot to new channel
# 2. In admin group, run: /setchannel @new_channel
```

### Add more admins
```bash
# Edit .env
ADMIN_IDS=123456789,987654321,555666777
# Restart: docker-compose restart
```

### Export all messages from a user
```bash
# In admin group, run:
/info @username
# Or by ID:
/info 123456789
# Bot sends Excel file with all their messages
```

## Performance Tuning

**For high volume:**
- Use webhooks (not polling)
- Set up multiple bot instances behind load balancer
- Monitor database size: `du -h data/anonymous.db`
- Archive old data if needed

**Database maintenance:**
```bash
# Optimize database
sqlite3 data/anonymous.db
> VACUUM;
> ANALYZE;
> .quit
```

## Security Tips

1. **Keep .env secret** - Never commit to git
2. **Rotate token if leaked** - Use @BotFather
3. **Use HTTPS only** - Telegram requires it
4. **Backup database regularly** - Contains submission data
5. **Delete old exports** - Excel files contain PII
6. **Monitor admin access** - Check who has mod rights

## Support

- Check logs: `docker-compose logs -f`
- Read WEBHOOK_SETUP.md for deployment
- Check anon.py comments for code details
- Test with polling mode if webhooks fail

---

**Pro Tip:** Use ngrok for free webhook testing!
```bash
bash webhook-dev.sh
```
