#!/bin/bash

# FerPs Anonymous Bot - Webhook Helper Script
# Makes it easy to run the bot with ngrok for local testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 FerPs Anonymous Bot - Webhook Helper${NC}"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED}❌ ngrok not found!${NC}"
    echo "Install from: https://ngrok.com/download"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env with your BOT_TOKEN and Supabase keys${NC}"
    exit 1
fi

# Check if BOT_TOKEN is set
if ! grep -q "BOT_TOKEN=your_bot_token_here" .env; then
    echo -e "${GREEN}✅ BOT_TOKEN is configured${NC}"
else
    echo -e "${RED}❌ BOT_TOKEN not set in .env${NC}"
    echo "Edit .env and set your BOT_TOKEN from @BotFather"
    exit 1
fi

# Check Supabase configuration
if grep -q "SUPABASE_URL=https://your-project.supabase.co" .env || grep -q "SUPABASE_SERVICE_ROLE_KEY=your-service-role-key" .env; then
    echo -e "${RED}❌ Supabase credentials not set in .env${NC}"
    echo "Edit .env and set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY"
    exit 1
else
    echo -e "${GREEN}✅ Supabase credentials are configured${NC}"
fi

echo -e "${BLUE}Starting ngrok tunnel on port 8080...${NC}"
echo ""

# Start ngrok in the background and capture the URL
ngrok_output=$(ngrok http 8080 --log=stdout 2>&1 &)
ngrok_pid=$!
sleep 2

# Get the ngrok URL
ngrok_url=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | cut -d'"' -f4 | head -n1)

if [ -z "$ngrok_url" ]; then
    echo -e "${RED}❌ Failed to get ngrok URL${NC}"
    kill $ngrok_pid 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✅ ngrok tunnel ready!${NC}"
echo -e "${BLUE}Public URL: ${YELLOW}$ngrok_url${NC}"
echo ""

# Update .env with ngrok URL
echo -e "${BLUE}Updating .env with webhook URL...${NC}"
sed -i.bak "s|^BASE_URL=.*|BASE_URL=$ngrok_url|" .env
echo -e "${GREEN}✅ .env updated${NC}"
echo ""

# Show environment
echo -e "${BLUE}🔧 Configuration:${NC}"
echo "   Base URL: $ngrok_url"
echo "   Webhook: $ngrok_url/webhook/telegram"
echo "   Local port: 8080"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found - run the bot locally instead:${NC}"
    echo "   pip install -r requirements.txt"
    echo "   python main.py"
else
    echo -e "${BLUE}Starting bot with Docker Compose...${NC}"
    docker-compose up
fi

# Cleanup on exit
trap "kill $ngrok_pid 2>/dev/null || true" EXIT
