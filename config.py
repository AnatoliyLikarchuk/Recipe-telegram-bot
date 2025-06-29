import os
from dotenv import load_dotenv

load_dotenv()

# Основные токены
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Новые AI провайдеры
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'deepseek').lower()  # deepseek, openai, mixed

# Проверка обязательных параметров
if not BOT_TOKEN:
    print("ОШИБКА: Токен бота не найден. Создайте файл .env и добавьте BOT_TOKEN=ваш_токен")
    exit(1)

if not DEEPSEEK_API_KEY:
    print("ОШИБКА: API ключ DeepSeek не найден. Добавьте DEEPSEEK_API_KEY=ваш_ключ в .env")
    exit(1)

# Информация о конфигурации AI
print(f"🤖 AI Провайдер: {AI_PROVIDER}")
if OPENAI_API_KEY:
    print("✅ OpenAI API ключ найден (резервный)")
else:
    print("⚠️ OpenAI API ключ не найден (будет использоваться только DeepSeek)")
    
print("✅ DeepSeek API ключ найден (основной)")