#!/usr/bin/env python3
"""Configuration for Telegram Bot."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env.bot.secret
env_path = Path(__file__).parent / ".env.bot.secret"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment from {env_path}")
else:
    print(f"Warning: {env_path} not found, using system environment variables")

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Backend configuration
LMS_API_URL = os.getenv("LMS_API_URL", "http://localhost:42002")
LMS_API_KEY = os.getenv("LMS_API_KEY")

# LLM configuration (for future tasks)
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1")
LLM_API_MODEL = os.getenv("LLM_API_MODEL", "coder-model")

# Validate required configuration
if not BOT_TOKEN:
    print("WARNING: BOT_TOKEN not set in .env.bot.secret")

if not LMS_API_KEY:
    print("WARNING: LMS_API_KEY not set in .env.bot.secret")