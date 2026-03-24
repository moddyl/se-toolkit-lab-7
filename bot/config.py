import os
from dotenv import load_dotenv

path = os.path.join(os.path.dirname(__file__), "..", ".env.bot.secret")
load_dotenv(dotenv_path=path)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
LMS_API_URL = os.getenv("LMS_API_URL", "http://localhost:8000")
LMS_API_KEY = os.getenv("LMS_API_KEY", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "http://localhost:42005")
LLM_API_MODEL = os.getenv("LLM_API_MODEL", "qwen-coder")