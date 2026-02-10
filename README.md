# FerPs Anonymous Bot

An anonymous submission bot for Telegram channels with admin moderation features.

## Features

✅ Users DM the bot with anonymous messages  
✅ Messages are posted anonymously to a public channel  
✅ Admin group receives messages with moderation buttons (delete, ban, view user profile)  
✅ Admin commands:
- `/setgroup` - Set the admin moderation group (run inside the group)
- `/setchannel @channel` - Set the public channel where posts are published
- `/user` - List all users who submitted messages
- `/info @username` or `/info user_id` - Export user's submissions as Excel file
- `/stats` - Show posting and ban statistics
- `/start` - User welcome message

## Setup

### 1. Create a Telegram Bot Token

Talk to [@BotFather](https://t.me/BotFather) on Telegram:
- `/start` → `/newbot` → follow prompts
- Copy your bot token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 2. Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:
```
BOT_TOKEN=your_token_here
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
BASE_URL=your_public_domain_or_ip
DEFAULT_CHANNEL=@your_channel
ADMIN_IDS=your_user_id
```

Make sure you've created the Supabase tables by running `SUPABASE_SCHEMA.sql`
in the Supabase SQL Editor (see `SUPABASE_SETUP.md`).

### 3. Get Your User ID

Send `/id` to [@userinfobot](https://t.me/userinfobot) on Telegram to find your user ID.

## Running the Bot

### Webhook Mode (Production - Recommended)

Requires a public domain and HTTPS:

```bash
# Set your public domain in .env
BASE_URL=https://yourdomain.com

# Run with Docker
docker-compose up -d
```

The webhook runs on port 8080 inside the container. You'll need to:
- Reverse proxy (nginx, Caddy) to handle HTTPS and forward to port 8080, OR
- Use ngrok for testing: `ngrok http 8080` then set `BASE_URL=https://your-ngrok-url.ngrok.io`

Or run locally:
```bash
pip install -r requirements.txt
python main.py
```

## Setting Up the Bot

1. Create a private **admin group** (can be small, just for you)
2. Add the bot to the group
3. Run `/setgroup` in the group → bot confirms
4. Create a public **channel** for anonymous posts
5. Add the bot to the channel
6. Run `/setchannel @channel_name` in the admin group

Now users can DM the bot → messages appear anonymously in the channel + show up in admin group with moderation buttons!

## Docker Deployment

### Using Docker Compose

```bash
docker-compose up -d
```

### Manual Docker

```bash
docker build -t ferps-anon .
docker run -d \
  --name ferps-anon \
  -e BOT_TOKEN=your_token \
  -e SUPABASE_URL=https://your-project.supabase.co \
  -e SUPABASE_SERVICE_ROLE_KEY=your-service-role-key \
  -e BASE_URL=https://yourdomain.com \
  -p 8080:8080 \
  ferps-anon
```

### Using ngrok for Webhook Testing

```bash
# Install ngrok: https://ngrok.com/download

# In one terminal:
ngrok http 8080

# In another terminal:
export BASE_URL=https://your-ngrok-url.ngrok.io
docker-compose up
```

## Database

Uses Supabase (PostgreSQL) for:
- User ↔ submission mapping
- Ban list
- Configuration (channel, group IDs, etc.)
- Export data for Excel reports

Make sure `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set in `.env`,
and the schema from `SUPABASE_SCHEMA.sql` has been applied.

## Admin Commands Reference

### Moderation
- **Delete button (🗑)** - Remove post from channel only
- **Ban button (🚫)** - Remove post + ban user from submitting
- **Profile button (👤)** - Open user's Telegram profile
- **Channel link button (🔗)** - Jump to post in channel

### Exports
```
/info @username     # Export all submissions from @username as Excel
/info 123456789     # Export by user ID
```

Excel file includes:
- Message content
- Timestamp (UTC)
- Message type (text, photo, video, etc.)
- Link to channel post
- Embedded images

## Health Check

```bash
curl http://localhost:8080/health
# {"status": "ok", "bot_token_set": true}
```

## Troubleshooting

### "Webhook not receiving updates"
- Make sure `BASE_URL` is publicly accessible
- Check that port 8080 is open/forwarded
- Verify HTTPS (Telegram requires HTTPS for webhooks)
- Check logs: `docker-compose logs -f`

### "Bot not in group/channel"
- Manually add the bot to both the admin group AND the public channel
- Run `/setgroup` in the group
- Run `/setchannel @channel` in the group

### "Can't post to channel"
- Make sure bot is admin in the channel
- Check that channel username starts with `@`
- Bot needs permission to post and edit messages

### "Database tables not found"
- Run `SUPABASE_SCHEMA.sql` in the Supabase SQL Editor
- Confirm `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env`

## Environment Variables

```
# Required
BOT_TOKEN              - Your Telegram bot token
SUPABASE_URL           - Supabase project URL
SUPABASE_SERVICE_ROLE_KEY - Supabase service role key

# Webhook config
BASE_URL              - Public URL where webhook is accessible
PORT                  - Port to listen on (default: 8080)

# Bot config
DEFAULT_CHANNEL       - Default channel (@name) for posts
ADMIN_IDS             - CSV of admin user IDs

# Optional
TZ                    - Timezone for timestamps
```

## License & Credits

Built for FerPs Anonymous community submissions.

---

Need help? Check the logs:
```bash
docker-compose logs -f ferps-anon-bot
```
