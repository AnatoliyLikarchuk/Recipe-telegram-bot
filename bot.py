import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from ai_helper import get_random_dish, generate_weekly_menu, format_weekly_menu, generate_daily_menu, format_daily_menu

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
            InlineKeyboardButton("🍽️ Меню на день", callback_data="daily_menu")
        ],
        [
            InlineKeyboardButton("📅 Меню на неделю", callback_data="weekly_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🍽️ *Привет! Я помощник по планированию меню для Тани!*

Я помогу решить вечную проблему "Что приготовить?"

Выбери что тебе нужно:
• 🎲 *Случайное блюдо* - предложу блюдо для завтрака, обеда или ужина
• 🍽️ *Меню на день* - составлю завтрак, обед и ужин на один день
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
    print(f"[BOT DEBUG] Запрос блюда для: {meal_type}")
    print(f"[BOT DEBUG] Callback data: {query.data}")
    
    # Показываем загрузку
    await query.edit_message_text("🤔 Думаю над блюдом...")
    
    try:
        print(f"[BOT DEBUG] Вызываем get_random_dish({meal_type})")
        dish = get_random_dish(meal_type)
        print(f"[BOT DEBUG] Получили блюдо: '{dish}'")
        
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
        print(f"[BOT DEBUG] Сообщение отправлено пользователю")
        
    except Exception as e:
        print(f"[BOT ERROR] Ошибка при получении блюда: {type(e).__name__}: {e}")
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

async def generate_daily_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сгенерировать меню на день"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🍽️ Составляю меню на день... ⏱️")
    
    try:
        menu = generate_daily_menu()
        menu_text = format_daily_menu(menu)
        
        keyboard = [
            [InlineKeyboardButton("🔄 Новое меню на день", callback_data="daily_menu")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Ошибка при генерации меню на день: {e}")
        await query.edit_message_text(
            "😕 Произошла ошибка при создании меню на день. Попробуй еще раз.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]])
        )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вернуться в главное меню"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("🎲 Случайное блюдо", callback_data="random_dish"),
            InlineKeyboardButton("🍽️ Меню на день", callback_data="daily_menu")
        ],
        [
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
    print(f"[BOT DEBUG] Нажата кнопка: {query.data}")
    print(f"[BOT DEBUG] От пользователя: {query.from_user.id}")
    
    if query.data == "random_dish":
        print("[BOT DEBUG] Переход к меню случайного блюда")
        await random_dish_menu(update, context)
    elif query.data == "daily_menu":
        print("[BOT DEBUG] Переход к генерации меню на день")
        await generate_daily_menu_handler(update, context)
    elif query.data == "weekly_menu":
        print("[BOT DEBUG] Переход к генерации меню на неделю")
        await generate_menu(update, context)
    elif query.data.startswith("dish_"):
        print(f"[BOT DEBUG] Запрос конкретного блюда: {query.data}")
        await get_dish_suggestion(update, context)
    elif query.data == "back_to_main":
        print("[BOT DEBUG] Возврат в главное меню")
        await back_to_main(update, context)
    else:
        print(f"[BOT WARNING] Неизвестная кнопка: {query.data}")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    print(f"[BOT DEBUG] Получено текстовое сообщение: '{update.message.text}'")
    print(f"[BOT DEBUG] От пользователя: {update.message.from_user.id}")
    
    keyboard = [
        [
            InlineKeyboardButton("🎲 Случайное блюдо", callback_data="random_dish"),
            InlineKeyboardButton("🍽️ Меню на день", callback_data="daily_menu")
        ],
        [
            InlineKeyboardButton("📅 Меню на неделю", callback_data="weekly_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 Привет! Я работаю только с кнопками.\n\nИспользуй кнопки ниже для выбора:",
        reply_markup=reply_markup
    )

def main():
    """Запуск бота"""
    print("🚀 Запускаю бота...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Устанавливаем команды бота для меню
    import asyncio
    async def set_commands():
        from telegram import BotCommand
        commands = [
            BotCommand("start", "🏠 Главное меню"),
        ]
        await application.bot.set_my_commands(commands)
    
    print("✅ Бот запущен и готов к работе!")
    
    # Устанавливаем команды и запускаем
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_commands())
    
    application.run_polling()

if __name__ == "__main__":
    main()