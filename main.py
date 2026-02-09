#!/usr/bin/env python3
"""
FastAPI webhook handler for FerPs Anonymous bot

This replaces the polling approach with webhooks for better performance and real-time updates.
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application

from anon import build_app
from database import init_db

load_dotenv(Path(__file__).resolve().parent / ".env")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
WEBHOOK_PATH = "/webhook/telegram"
PORT = int(os.getenv("PORT", 8080))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Put it in .env")

app = FastAPI(title="FerPs Anonymous Bot")
app_telegram: Optional[Application] = None


@app.on_event("startup")
async def on_startup():
    """Initialize the Telegram bot and set webhook."""
    global app_telegram
    
    # Initialize database
    await init_db()
    
    app_telegram = build_app()
    await app_telegram.initialize()
    
    webhook_url = f"{BASE_URL}{WEBHOOK_PATH}"
    log.info(f"Setting webhook to: {webhook_url}")
    
    try:
        await app_telegram.bot.set_webhook(
            url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
        log.info("✅ Webhook set successfully")
    except Exception as e:
        log.error(f"❌ Failed to set webhook: {e}")
        raise


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
