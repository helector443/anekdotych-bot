import requests
import json
import time
from config import Config

class OpenRouterClient:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.api_url = Config.OPENROUTER_API_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://t.me/anekdotych_bot",
            "X-Title": "Anekdotych Telegram Bot"
        }
        self.last_request_time = 0
        self.request_cooldown = Config.REQUEST_COOLDOWN
    
    def generate_joke(self, theme=None):
        """Генерация анекдота через OpenRouter"""
        
        # Защита от слишком частых запросов
        current_time = time.time()
        if current_time - self.last_request_time < self.request_cooldown:
            time.sleep(self.request_cooldown - (current_time - self.last_request_time))
        
        prompt = self._build_prompt(theme)
        
        payload = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 250,
            "temperature": 0.85,
            "top_p": 0.9
        }
        
        try:
            print("🔄 Отправка запроса к OpenRouter API...")
            self.last_request_time = time.time()
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"📊 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                joke = result['choices'][0]['message']['content'].strip()
                tokens_used = result.get('usage', {}).get('total_tokens', 0)
                return joke, tokens_used
            else:
                error_msg = f"❌ Ошибка API ({response.status_code})"
                if response.status_code == 429:
                    error_msg += ": Превышен лимит запросов"
                return error_msg, 0
                
        except Exception as e:
            return f"❌ Ошибка: {str(e)}", 0
    
    def _build_prompt(self, theme):
        """Построение промпта"""
        if theme:
            return f'''Напиши смешной анекдот на тему "{theme}". 
Требования:
- Длина: 2-4 предложения
- Стиль: классический русский анекдот
- Без оскорблений, политики и черного юмора
- Естественный и смешной сюжет'''
        else:
            return '''Напиши случайный смешной анекдот. 
Требования:
- Длина: 2-4 предложения  
- Стиль: классический русский анекдот
- Без оскорблений, политики и черного юмора
- Естественный и смешной сюжет'''
    
    def _get_system_prompt(self):
        """Системный промпт"""
        return """Ты - мастер юмора и анекдотов. Твоя задача - создавать короткие, смешные анекдоты в стиле классических русских анекдотов.
        
Правила:
1. Длина: 2-4 предложения
2. Стиль: естественный разговорный русский язык
3. Темы: повседневные ситуации, работа, учеба, семья, животные
4. Запрещено: оскорбления, политика, черный юмор, дискриминация
5. Юмор: легкий, понятный, с неожиданной развязкой

Пример хорошего анекдота:
"Приходит программист в магазин и спрашивает:
- У вас есть батарейки?
- Есть.
- А без них можно?"

Всегда старайся создать оригинальный и смешной анекдот!"""
    
    def generate_random_joke(self):
        """Генерация случайного анекдота"""
        themes = [
            "программисты", "студенты", "семья", "работа", 
            "животные", "школа", "друзья", "технологии",
            "еда", "отпуск", "спорт", "музыка", "математика",
            "физика", "рыбалка", "погода", "деньги", "хобби",
            "кошки", "собаки", "путешествия", "шоппинг"
        ]
        import random
        theme = random.choice(themes)
        return self.generate_joke(theme)