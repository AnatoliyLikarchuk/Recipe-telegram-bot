from config import OPENAI_API_KEY, DEEPSEEK_API_KEY, AI_PROVIDER
from memory_manager import dish_memory
from prompt_variations import prompt_generator
from ai_clients import MultiAIClient

import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация универсального AI клиента
try:
    client = MultiAIClient(
        openai_key=OPENAI_API_KEY,
        deepseek_key=DEEPSEEK_API_KEY,
        provider=AI_PROVIDER
    )
    logger.info(f"🤖 AI клиент инициализирован: {client.get_active_provider()}")
except Exception as e:
    logger.error(f"Ошибка инициализации AI клиента: {e}")
    # Fallback на простой OpenAI клиент
    from ai_clients import OpenAIClient
    client = OpenAIClient(OPENAI_API_KEY)
    logger.warning("⚠️ Используется fallback OpenAI клиент")

def get_random_dish(meal_type):
    """Получить случайное блюдо для завтрака, обеда или ужина"""
    
    # Получаем список блюд для избежания
    avoid_text = dish_memory.get_avoid_list_text(meal_type)
    logger.info(f"[AI DEBUG] Избегаем для {meal_type}: {avoid_text}")
    
    # Проверяем API ключ
    api_key = os.getenv('OPENAI_API_KEY') or OPENAI_API_KEY
    if not api_key or api_key == 'your_openai_key_here':
        logger.error("[AI ERROR] OpenAI API ключ не найден или не установлен!")
        return "Омлет с овощами"
    
    logger.info(f"[AI DEBUG] API ключ найден, длина: {len(api_key)} символов")
    
    # Генерируем случайный промпт с учетом избегаемых блюд
    prompt = prompt_generator.get_random_prompt(meal_type, avoid_text)
    logger.info(f"[AI DEBUG] Промпт: {prompt[:100]}...")
    
    try:
        logger.info("[AI DEBUG] Отправляем запрос к AI...")
        dish_name = client.get_completion(
            prompt=prompt,
            max_tokens=50,
            temperature=0.9
        )
        
        logger.info(f"[AI DEBUG] Ответ AI: '{dish_name}'")
        
        # Проверяем что ответ не пустой
        if not dish_name:
            logger.warning("[AI DEBUG] Пустой ответ от AI!")
            return "Омлет с овощами"
        
        # Сохраняем блюдо в память для избежания повторов
        dish_memory.add_dish(meal_type, dish_name)
        logger.info(f"[AI DEBUG] Сохранено в память: {dish_name}")
        
        return dish_name
        
    except Exception as e:
        logger.error(f"[AI ERROR] Ошибка AI: {type(e).__name__}: {e}")
        logger.error(f"[AI ERROR] Полная ошибка: {str(e)}")
        return "Омлет с овощами"  # fallback вариант

def generate_weekly_menu():
    """Сгенерировать меню на неделю"""
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    menu = {}
    
    for day in days:
        menu[day] = {
            "завтрак": get_random_dish("завтрак"),
            "обед": get_random_dish("обед"), 
            "ужин": get_random_dish("ужин")
        }
    
    return menu

def format_weekly_menu(menu):
    """Отформатировать меню для отправки в телеграм"""
    text = "🍽️ *Меню на неделю:*\n\n"
    
    for day, meals in menu.items():
        text += f"*{day}:*\n"
        text += f"🌅 Завтрак: {meals['завтрак']}\n"
        text += f"☀️ Обед: {meals['обед']}\n"
        text += f"🌙 Ужин: {meals['ужин']}\n\n"
    
    return text