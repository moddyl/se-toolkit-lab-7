from dotenv import load_dotenv
import os

# Загружаем .env файл
load_dotenv('.env.bot.secret')

print("=== Проверка загрузки .env ===")
print(f"BOT_TOKEN: {os.getenv('BOT_TOKEN')}")
print(f"LMS_API_URL: {os.getenv('LMS_API_URL')}")
print(f"LMS_API_KEY: {os.getenv('LMS_API_KEY')}")