import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN
from ai_helper import get_random_dish, generate_weekly_menu, format_weekly_menu

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    keyboard = [
        [
            InlineKeyboardButton("🎲 Случайное блюдо", callback_data="random_dish"),
            InlineKeyboardButton("📅 Меню на неделю", callback_data="weekly_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🍽️ *Привет! Я помощник по планированию меню для Тани!*

Я помогу решить вечную проблему "Что приготовить?"

Выбери что тебе нужно:
• 🎲 *Случайное блюдо* - предложу блюдо для завтрака, обеда или ужина
• 📅 *Меню на неделю* - составлю полное меню на всю неделю
    """
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=reply_markup, 
        parse_mode='Markdown'
    )

async def random_dish_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать меню выбора типа блюда"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🌅 Завтрак", callback_data="dish_завтрак")],
        [InlineKeyboardButton("☀️ Обед", callback_data="dish_обед")],
        [InlineKeyboardButton("🌙 Ужин", callback_data="dish_ужин")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎲 *Выбери категорию блюда:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def get_dish_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получить предложение блюда от ИИ"""
    query = update.callback_query
    await query.answer()
    
    meal_type = query.data.replace("dish_", "")
    
    # Показываем загрузку
    await query.edit_message_text("🤔 Думаю над блюдом...")
    
    try:
        dish = get_random_dish(meal_type)
        
        keyboard = [
            [InlineKeyboardButton("🔄 Другое блюдо", callback_data=f"dish_{meal_type}")],
            [InlineKeyboardButton("⬅️ Назад к категориям", callback_data="random_dish")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        emoji_map = {"завтрак": "🌅", "обед": "☀️", "ужин": "🌙"}
        
        await query.edit_message_text(
            f"{emoji_map[meal_type]} *{meal_type.capitalize()}:*\n\n🍽️ *{dish}*\n\nНравится предложение?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Ошибка при получении блюда: {e}")
        await query.edit_message_text(
            "😕 Произошла ошибка. Попробуй еще раз.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="random_dish")]])
        )

async def generate_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сгенерировать меню на неделю"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🍽️ Составляю меню на неделю... Это займет немного времени ⏱️")
    
    try:
        menu = generate_weekly_menu()
        menu_text = format_weekly_menu(menu)
        
        keyboard = [
            [InlineKeyboardButton("🔄 Новое меню", callback_data="weekly_menu")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Ошибка при генерации меню: {e}")
        await query.edit_message_text(
            "😕 Произошла ошибка при создании меню. Попробуй еще раз.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]])
        )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вернуться в главное меню"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🎲 Случайное блюдо", callback_data="random_dish"),
            InlineKeyboardButton("📅 Меню на неделю", callback_data="weekly_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🍽️ *Главное меню*\n\nЧто тебе нужно?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик всех кнопок"""
    query = update.callback_query
    
    if query.data == "random_dish":
        await random_dish_menu(update, context)
    elif query.data == "weekly_menu":
        await generate_menu(update, context)
    elif query.data.startswith("dish_"):
        await get_dish_suggestion(update, context)
    elif query.data == "back_to_main":
        await back_to_main(update, context)

def main():
    """Запуск бота"""
    print("🚀 Запускаю бота...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Бот запущен и готов к работе!")
    application.run_polling()

if __name__ == "__main__":
    main()