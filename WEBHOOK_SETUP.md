# Webhook Setup Guide

## Quick Start with ngrok (Testing)

Perfect for local testing without a public domain:

```bash
# 1. Install ngrok from https://ngrok.com/download

# 2. Start ngrok in one terminal:
ngrok http 8080

# Copy your ngrok URL (looks like: https://abc123.ngrok.io)

# 3. In .env, set:
BOT_TOKEN=your_token
BASE_URL=https://abc123.ngrok.io    # Your ngrok URL
USE_POLLING=false

# 4. In another terminal, run:
docker-compose up

# Bot is now running with webhook!
```

## Production Deployment

### Option 1: Using Nginx Reverse Proxy

Requirements:
- Public domain with DNS pointing to your server
- SSL certificate (Let's Encrypt recommended)

```nginx
# /etc/nginx/sites-available/ferps-anon
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/ferps-anon /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Setup SSL:
```bash
# Using Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
```

Then set in `.env`:
```
BASE_URL=https://yourdomain.com
USE_POLLING=false
PORT=8080
```

And run:
```bash
docker-compose up -d
```

### Option 2: Using Caddy (Simpler!)

Caddy automatically handles SSL certificates:

```bash
# Install Caddy
sudo apt install caddy

# Edit Caddyfile
sudo nano /etc/caddy/Caddyfile
```

Add:
```caddyfile
yourdomain.com {
    reverse_proxy localhost:8080
}
```

Restart:
```bash
sudo systemctl restart caddy
```

Then set in `.env`:
```
BASE_URL=https://yourdomain.com
```

### Option 3: Docker with Let's Encrypt

Use docker-compose with auto-renewing SSL:

```yaml
version: "3.9"

services:
  ferps-anon-bot:
    build: .
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./data:/data
    environment:
      - TZ=UTC
      - DB_PATH=/data/anonymous.db
      - PORT=8080
      - BASE_URL=https://yourdomain.com
      - USE_POLLING=false
    # Don't expose port (reverse proxy will handle it)

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - ferps-anon-bot

  certbot:
    image: certbot/certbot
    restart: unless-stopped
    volumes:
      - ./certs:/etc/letsencrypt
      - ./certbot-challenge:/var/www/certbot
    entrypoint: >
      /bin/sh -c "trap exit TERM; while :; do 
        certbot renew --webroot -w /var/www/certbot;
        sleep 86400;
      done"
```

## Webhook Health Checks

Verify webhook is working:

```bash
# Check if bot is running
curl https://yourdomain.com/health
# {"status": "ok", "bot_token_set": true}

# Check webhook status with Telegram API
curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"
```

Expected output:
```json
{
  "ok": true,
  "result": {
    "url": "https://yourdomain.com/webhook/telegram",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "ip_address": "1.2.3.4",
    "last_error_date": 0,
    "max_connections": 40
  }
}
```

## Monitoring

Check logs:
```bash
# Docker
docker-compose logs -f ferps-anon-bot

# Direct
tail -f /var/log/syslog | grep ferps
```

Common webhook issues:
- **"pending_update_count"** increasing → Bot isn't processing updates
  - Check logs for errors
  - Verify database isn't locked
- **"last_error_date"** recent → Telegram couldn't reach webhook
  - Check firewall/port forwarding
  - Verify BASE_URL is correct
  - Test: `curl https://yourdomain.com/health`

## Switching Between Modes

Switch from polling to webhook:
```bash
# Edit .env
- USE_POLLING=true
+ USE_POLLING=false

# Update BASE_URL
+ BASE_URL=https://yourdomain.com

# Restart
docker-compose restart
```

Switch back to polling (if needed):
```bash
# Edit .env
+ USE_POLLING=true

# Restart
docker-compose restart
```

## Performance Tips

1. **Use HTTPS only** - Telegram requires it for webhooks
2. **High availability** - Run multiple bot instances behind a load balancer
3. **Monitor webhook queue** - Check `pending_update_count` regularly
4. **Database backups** - Backup `/data/anonymous.db` regularly
5. **Rate limiting** - Bot comes with built-in rate limiter (python-telegram-bot)

## Troubleshooting

### Webhook updates not working
```bash
# 1. Check if webhook is set
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# 2. Check if URL is accessible
curl -v https://yourdomain.com/health

# 3. Check bot logs
docker-compose logs -f

# 4. Verify firewall allows 443 (HTTPS)
sudo ufw allow 443/tcp
```

### Falling back to polling
If webhook isn't working, temporarily use polling:
```bash
# Edit .env
USE_POLLING=true

# Restart
docker-compose restart
```

Then debug webhook setup.

### Database locked error
```bash
# Check processes
lsof | grep anonymous.db

# Force restart
docker-compose restart
```
