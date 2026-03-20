#!/usr/bin/env python3
"""Telegram Bot for LMS - entry point with --test mode."""

import sys
import argparse
import logging
from telegram.ext import Application, CommandHandler
from handlers import start_handler, help_handler, health_handler
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_response(command: str, args: str = "") -> str:
    """Route command to appropriate handler and return response."""
    cmd = command.lower()
    
    if cmd == "/start":
        return start_handler()
    elif cmd == "/help":
        return help_handler()
    elif cmd == "/health":
        return health_handler()
    else:
        return f"Unknown command: {command}"

def run_test_mode(command: str):
    """Run in test mode: print response to stdout and exit."""
    response = get_response(command)
    print(response)
    sys.exit(0)

def run_bot():
    """Run the bot normally (Telegram mode)."""
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)
    
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text(start_handler())))
    app.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(help_handler())))
    app.add_handler(CommandHandler("health", lambda u, c: u.message.reply_text(health_handler())))
    
    logger.info("Starting bot...")
    app.run_polling(allowed_updates=["message"])

def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument("--test", help="Run in test mode with a command (e.g., --test '/start')")
    args = parser.parse_args()
    
    if args.test:
        run_test_mode(args.test)
    else:
        run_bot()

if __name__ == "__main__":
    main()