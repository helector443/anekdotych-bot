import logging
from telegram import Update
from telegram.ext import ContextTypes
from openrouter_client import OpenRouterClient
from database import Database
from config import Config
from utils.helpers import split_message

db = Database()
joke_client = OpenRouterClient()

async def handle_joke_request(update: Update, context: ContextTypes.DEFAULT_TYPE, theme: str):
    """Обработка запроса на генерацию анекдота"""
    user = update.effective_user
    
    # Проверяем лимиты
    if not db.can_make_request(user.id):
        await update.message.reply_text(
            f"⚠️ Вы превысили дневной лимит ({Config.MAX_REQUESTS_PER_USER} запросов). "
            "Попробуйте завтра!"
        )
        return
    
    try:
        await update.message.reply_text(f"🎭 Генерирую анекдот на тему '{theme}'...")
        
        joke, tokens_used = joke_client.generate_joke(theme)
        
        if joke.startswith(('❌', '⚠️')):
            await update_message_with_retry(update, joke)
        else:
            # Логируем успешный запрос
            db.log_request(user.id, theme, joke, tokens_used)
            
            # Отправляем анекдот частями если он длинный
            message_parts = split_message(joke, Config.MAX_MESSAGE_LENGTH)
            for part in message_parts:
                await update_message_with_retry(update, part)
                
    except Exception as e:
        logging.error(f"Error in handle_joke_request: {e}")
        await update_message_with_retry(update, "😞 Произошла непредвиденная ошибка. Попробуйте позже.")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user = update.effective_user
    user_message = update.message.text.strip()
    
    # Игнорируем короткие сообщения
    if len(user_message) < 2:
        return
    
    await handle_joke_request(update, context, user_message)

async def update_message_with_retry(update: Update, text: str, max_retries: int = 3):
    """Отправка сообщения с повторными попытками"""
    for attempt in range(max_retries):
        try:
            await update.message.reply_text(text)
            return
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"Failed to send message after {max_retries} attempts: {e}")
                raise
            logging.warning(f"Attempt {attempt + 1} failed, retrying...")