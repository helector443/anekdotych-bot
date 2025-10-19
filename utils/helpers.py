import re
import time
from typing import List, Tuple
from config import Config

def split_message(text: str, max_length: int = None) -> List[str]:
    """
    Разбивает текст на части указанной максимальной длины.
    Старается разбивать по предложениям, а не по словам.
    """
    if max_length is None:
        max_length = Config.MAX_MESSAGE_LENGTH
    
    if len(text) <= max_length:
        return [text]
    
    # Пытаемся разбить по предложениям
    sentences = re.split(r'([.!?]+[\s]*)', text)
    parts = []
    current_part = ""
    
    i = 0
    while i < len(sentences):
        sentence = sentences[i]
        
        # Если предложение само по себе слишком длинное
        if len(sentence) > max_length:
            # Разбиваем по словам
            words = sentence.split()
            for word in words:
                if len(current_part) + len(word) + 1 <= max_length:
                    current_part += word + " "
                else:
                    if current_part:
                        parts.append(current_part.strip())
                    current_part = word + " "
            i += 1
            continue
        
        # Обычное предложение
        if len(current_part) + len(sentence) <= max_length:
            current_part += sentence
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = sentence
        i += 1
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts

def validate_theme(theme: str) -> Tuple[bool, str]:
    """
    Проверяет тему на валидность.
    Возвращает (is_valid, error_message)
    """
    if not theme or len(theme.strip()) == 0:
        return False, "Тема не может быть пустой"
    
    theme = theme.strip()
    
    # Проверка длины
    if len(theme) > 100:
        return False, "Тема слишком длинная (максимум 100 символов)"
    
    if len(theme) < 2:
        return False, "Тема слишком короткая (минимум 2 символа)"
    
    # Проверка на запрещенные символы
    forbidden_chars = r'[<>{}|\\^`]'
    if re.search(forbidden_chars, theme):
        return False, "Тема содержит запрещенные символы"
    
    # Проверка на повторяющиеся слова (анти-спам)
    words = theme.split()
    if len(words) > 10:
        return False, "Слишком много слов в теме (максимум 10)"
    
    return True, ""

def format_user_stats(stats_data) -> str:
    """Форматирует статистику пользователя в красивый текст"""
    if not stats_data:
        return "📊 Статистика недоступна"
    
    request_count, last_request = stats_data
    last_request_str = last_request[:16] if last_request else "еще нет"
    
    return f"""
📊 Ваша статистика:

🔄 Всего запросов: {request_count}
⏰ Последний запрос: {last_request_str}
📅 Лимит: {Config.MAX_REQUESTS_PER_USER} в день

🎭 Продолжайте наслаждаться анекдотами!
    """.strip()

def rate_limit_check(user_id: int, db) -> Tuple[bool, str]:
    """
    Проверяет лимиты запросов для пользователя.
    Возвращает (can_make_request, error_message)
    """
    if not db.can_make_request(user_id):
        return False, f"⚠️ Вы превысили дневной лимит ({Config.MAX_REQUESTS_PER_USER} запросов). Попробуйте завтра!"
    
    return True, ""

def clean_joke_text(text: str) -> str:
    """Очищает текст анекдота от лишних пробелов и форматирования"""
    if not text:
        return ""
    
    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text)
    
    # Убираем пробелы в начале и конце
    text = text.strip()
    
    # Заменяем множественные переносы строк на двойные
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text

def get_theme_emoji(theme: str) -> str:
    """Возвращает эмодзи для темы"""
    theme_emojis = {
        'программист': '💻',
        'студент': '🎓', 
        'семья': '👨‍👩‍👧‍👦',
        'работа': '💼',
        'животные': '🐾',
        'школа': '🏫',
        'друг': '👥',
        'технология': '🔧',
        'еда': '🍕',
        'отпуск': '🏖️',
        'спорт': '⚽',
        'музыка': '🎵',
        'математика': '📐',
        'физика': '⚛️',
        'рыбалка': '🎣',
        'погода': '🌤️',
        'деньги': '💰',
        'хобби': '🎨',
        'кот': '🐱',
        'собака': '🐶',
        'путешествия': '✈️',
        'шоппинг': '🛍️'
    }
    
    theme_lower = theme.lower()
    for key, emoji in theme_emojis.items():
        if key in theme_lower:
            return emoji
    
    return '🎭'  # Эмодзи по умолчанию