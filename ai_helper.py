from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_random_dish(meal_type):
    """Получить случайное блюдо для завтрака, обеда или ужина"""
    prompt = f"""
    Ты - персональный кулинарный помощник Тани. Твоя единственная задача - предлагать простые и вкусные блюда для домашнего приготовления.
    
    Категория: {meal_type}
    
    Требования:
    - Предложи ТОЛЬКО ОДНО блюдо
    - Отвечай ТОЛЬКО названием блюда (максимум 4-5 слов)
    - Блюдо должно быть простым для домашнего приготовления
    - Учитывай русскую/европейскую кухню
    - Никаких объяснений и инструкций
    
    Пример ответа: "Омлет с помидорами"
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Ошибка OpenAI: {e}")
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