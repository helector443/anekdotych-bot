import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # OpenRouter
    OPENROUTER_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    # Настройки бота
    BOT_USERNAME = "anekdotych_bot"
    MAX_MESSAGE_LENGTH = 4096
    
    # Статистика и мониторинг
    ADMIN_IDS = [123456789]  # Замените на ваш ID в Telegram
    
    # Лимиты
    MAX_REQUESTS_PER_USER = 50  # Максимум запросов в день на пользователя
    REQUEST_COOLDOWN = 5  # Секунды между запросами