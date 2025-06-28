import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not BOT_TOKEN:
    print("ОШИБКА: Токен бота не найден. Создайте файл .env и добавьте BOT_TOKEN=ваш_токен")
    exit(1)

if not OPENAI_API_KEY:
    print("ОШИБКА: API ключ OpenAI не найден. Добавьте OPENAI_API_KEY=ваш_ключ в .env")
    exit(1)