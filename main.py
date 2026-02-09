#!/usr/bin/env python3
"""
FastAPI webhook handler for FerPs Anonymous bot

This replaces the polling approach with webhooks for better performance and real-time updates.
"""
import os
import logging
import asyncio
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application
from telegram.error import RetryAfter

from anon import build_app
from database import init_db

load_dotenv(Path(__file__).resolve().parent / "data" / ".env")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
WEBHOOK_PATH = "/webhook/telegram"
PORT = int(os.getenv("PORT", 8080))

if not BOT_TOKEN:
    log.warning("BOT_TOKEN is missing. Telegram bot will not be initialized until a valid token is provided in .env")

app = FastAPI(title="FerPs Anonymous Bot")
app_telegram: Optional[Application] = None


@app.on_event("startup")
async def on_startup():
    """Initialize the Telegram bot and set webhook."""
    global app_telegram
    
    # Initialize database
    await init_db()
    
    # Initialize Telegram bot only if token is present
    if BOT_TOKEN:
        try:
            app_telegram = build_app()
            await app_telegram.initialize()

            webhook_url = f"{BASE_URL}{WEBHOOK_PATH}"
            log.info(f"Setting webhook to: {webhook_url}")

            # Retry logic for rate limiting with exponential backoff
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    await app_telegram.bot.set_webhook(
                        url=webhook_url,
                        allowed_updates=Update.ALL_TYPES,
                        drop_pending_updates=True,
                    )
                    log.info("✅ Webhook set successfully")
                    break
                except RetryAfter as e:
                    wait_time = max(e.retry_after, 1) + (2 ** attempt)  # At least retry_after + exponential backoff
                    if attempt < max_retries - 1:
                        log.warning(f"Rate limited (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                    else:
                        log.error(f"Max retries exceeded. Rate limit error: {e}")
                        raise
        except Exception as e:
            log.error(f"❌ Telegram initialization failed: {e}")
            log.warning("Continuing without Telegram bot. Provide a valid BOT_TOKEN to enable it.")
            app_telegram = None


@app.on_event("shutdown")
async def on_shutdown():
    """Clean up the Telegram bot."""
    global app_telegram
    if app_telegram:
        await app_telegram.stop()


@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    """Webhook endpoint that receives updates from Telegram."""
    try:
        if not app_telegram:
            return {"ok": False, "error": "Telegram bot is not initialized"}

        data = await request.json()
        update = Update.de_json(data, app_telegram.bot)

        if update:
            log.debug(f"Received update: {update.update_id}")
            await app_telegram.process_update(update)

        return {"ok": True}
    except Exception as e:
        log.error(f"Error processing webhook: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "bot_token_set": bool(BOT_TOKEN)}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "FerPs Anonymous Bot",
        "mode": "webhook",
        "webhook_path": WEBHOOK_PATH,
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    log.info(f"Starting FerPs Anonymous bot on 0.0.0.0:{PORT}")
    log.info(f"Webhook endpoint: {BASE_URL}{WEBHOOK_PATH}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
    )
