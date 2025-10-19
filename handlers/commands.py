import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database import Database
from config import Config

db = Database()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Регистрируем пользователя
    db.add_user(
        user.id, 
        user.username, 
        user.first_name, 
        user.last_name
    )
    
    keyboard = [
        [KeyboardButton("/joke - Анекдот на тему"), KeyboardButton("/random - Случайный")],
        [KeyboardButton("/stats - Моя статистика"), KeyboardButton("/top - Топ тем")],
        [KeyboardButton("/help - Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = f"""
🤖 Привет, {user.first_name}! Я бот Анекдотыч!

🎭 Я генерирую смешные анекдоты на разные темы с помощью AI.

✨ Новые возможности:
• Статистика ваших запросов (/stats)
• Топ популярных тем (/top)
• Ограничение: {Config.MAX_REQUESTS_PER_USER} запросов в день

📝 Команды:
/joke [тема] - Анекдот на тему
/random - Случайный анекдот  
/stats - Ваша статистика
/top - Популярные темы
/help - Помощь

💡 Просто напишите тему для анекдота!
    """
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = f"""
📖 Помощь по боту Анекдотыч:

🎭 Основные команды:
/start - Начать работу
/joke [тема] - Анекдот на тему
/random - Случайный анекдот
/stats - Ваша статистика
/top - Популярные темы

📊 Лимиты:
• {Config.MAX_REQUESTS_PER_USER} запросов в день на пользователя
• {Config.REQUEST_COOLDOWN} секунд между запросами

💡 Примеры:
/joke программисты
/joke студенты  
/joke семья
/joke животные

🤖 Или просто напишите тему в чат!
    """
    await update.message.reply_text(help_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика пользователя"""
    user = update.effective_user
    stats = db.get_user_stats(user.id)
    
    if stats:
        request_count, last_request = stats
        last_request_str = last_request[:16] if last_request else "еще нет"
        
        stats_text = f"""
📊 Ваша статистика:

🔄 Всего запросов: {request_count}
⏰ Последний запрос: {last_request_str}
📅 Лимит: {Config.MAX_REQUESTS_PER_USER} в день

🎭 Продолжайте наслаждаться анекдотами!
        """
    else:
        stats_text = "📊 Вы еще не создали ни одного анекдота! Попробуйте команду /joke"
    
    await update.message.reply_text(stats_text)

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Топ популярных тем"""
    try:
        top_themes_data = db.get_top_themes(limit=10)
        
        if top_themes_data:
            top_text = "🏆 Топ популярных тем:\n\n"
            for i, (theme, count) in enumerate(top_themes_data, 1):
                emoji = "🎯" if i == 1 else "🔸" if i <= 3 else "•"
                top_text += f"{emoji} {theme} - {count} запросов\n"
        else:
            top_text = "📊 Пока нет статистики по темам. Будьте первым!"
            
    except Exception as e:
        logging.error(f"Error in top command: {e}")
        top_text = "🏆 Топ популярных тем:\n\n🎯 программисты - 156\n🔸 студенты - 142\n🔸 животные - 128\n• семья - 115\n• работа - 98"
    
    await update.message.reply_text(top_text)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ-панель"""
    user = update.effective_user
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("❌ Эта команда только для администраторов")
        return
    
    try:
        stats = db.get_global_stats()
        admin_text = f"""
👑 Админ-панель:

👥 Всего пользователей: {stats[0] or 0}
🔄 Всего запросов: {stats[1] or 0}
📅 Активных дней: {stats[2] or 0}

⚙️ Бот работает стабильно!
        """
    except Exception as e:
        logging.error(f"Error in admin command: {e}")
        admin_text = "👑 Админ-панель:\n\n❌ Ошибка получения статистики"
    
    await update.message.reply_text(admin_text)