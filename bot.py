import logging
import time
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    ContextTypes, filters, CallbackContext
)

from handlers.commands import (
    start_command, help_command, stats_command, 
    top_command, admin_command
)
from handlers.messages import handle_text_message, handle_joke_request
from database import Database
from config import Config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class AnekdotychBot:
    def __init__(self):
        self.db = Database()
        self.application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
        self.setup_handlers()
        self.setup_jobs()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        
        # Основные команды
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("stats", stats_command))
        self.application.add_handler(CommandHandler("top", top_command))
        self.application.add_handler(CommandHandler("admin", admin_command))
        self.application.add_handler(CommandHandler("joke", self.joke_command))
        self.application.add_handler(CommandHandler("random", self.random_joke_command))
        
        # Обработка текстовых сообщений
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            handle_text_message
        ))
    
    def setup_jobs(self):
        """Настройка фоновых задач"""
        job_queue = self.application.job_queue
        # Проверка здоровья каждые 30 минут
        job_queue.run_repeating(self.health_check, interval=1800, first=10)
    
    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /joke"""
        if context.args:
            theme = ' '.join(context.args)
            await handle_joke_request(update, context, theme)
        else:
            await update.message.reply_text("🎭 Укажите тему для анекдота!\nПример: /joke программисты")
    
    async def random_joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /random"""
        await handle_joke_request(update, context, "random")
    
    async def health_check(self, context: CallbackContext):
        """Проверка здоровья бота"""
        try:
            # Простой тест базы данных
            stats = self.db.get_global_stats()
            logging.info("✅ Health check passed")
        except Exception as e:
            logging.error(f"❌ Health check failed: {e}")
    
    def run(self):
        """Запуск бота"""
        print("🤖 Бот Анекдотыч запущен!")
        print("🔑 Проверка конфигурации...")
        print(f"Telegram Token: {'✅' if Config.TELEGRAM_TOKEN else '❌'}")
        print(f"OpenRouter API Key: {'✅' if Config.OPENROUTER_API_KEY else '❌'}")
        print(f"Database: {'✅' if self.db else '❌'}")
        print("🚀 Бот готов к работе 24/7!")
        
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = AnekdotychBot()
    bot.run()