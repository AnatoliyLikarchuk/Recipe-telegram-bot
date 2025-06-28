from openai import OpenAI
from config import OPENAI_API_KEY
from memory_manager import dish_memory
from prompt_variations import prompt_generator

# Инициализация клиента с минимальными параметрами для Railway
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    print(f"Ошибка инициализации OpenAI: {e}")
    # Fallback для Railway окружения
    import os
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY', OPENAI_API_KEY),
        timeout=30.0
    )

def get_random_dish(meal_type):
    """Получить случайное блюдо для завтрака, обеда или ужина"""
    
    # Получаем список блюд для избежания
    avoid_text = dish_memory.get_avoid_list_text(meal_type)
    print(f"[DEBUG] Избегаем для {meal_type}: {avoid_text}")
    
    # Генерируем случайный промпт с учетом избегаемых блюд
    prompt = prompt_generator.get_random_prompt(meal_type, avoid_text)
    print(f"[DEBUG] Промпт: {prompt[:100]}...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.9,  # Уменьшаем для стабильности
            top_p=0.9         # Контроль качества
        )
        
        dish_name = response.choices[0].message.content.strip()
        print(f"[DEBUG] Ответ OpenAI: '{dish_name}'")
        
        # Проверяем что ответ не пустой
        if not dish_name:
            print("[DEBUG] Пустой ответ от OpenAI!")
            return "Омлет с овощами"
        
        # Сохраняем блюдо в память для избежания повторов
        dish_memory.add_dish(meal_type, dish_name)
        print(f"[DEBUG] Сохранено в память: {dish_name}")
        
        return dish_name
        
    except Exception as e:
        print(f"[ERROR] Ошибка OpenAI: {type(e).__name__}: {e}")
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