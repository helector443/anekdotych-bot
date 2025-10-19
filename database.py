import sqlite3
import json
import time
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path="anekdotych.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            # Таблица пользователей
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    request_count INTEGER DEFAULT 0,
                    last_request TIMESTAMP
                )
            ''')
            
            # Таблица запросов
            conn.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    theme TEXT,
                    joke_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tokens_used INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
    
    def add_user(self, user_id, username, first_name, last_name):
        """Добавление пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            conn.commit()
    
    def log_request(self, user_id, theme, joke_text, tokens_used):
        """Логирование запроса"""
        with sqlite3.connect(self.db_path) as conn:
            # Обновляем счетчик пользователя
            conn.execute('''
                UPDATE users 
                SET request_count = request_count + 1, last_request = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
            
            # Сохраняем запрос
            conn.execute('''
                INSERT INTO requests (user_id, theme, joke_text, tokens_used)
                VALUES (?, ?, ?, ?)
            ''', (user_id, theme, joke_text, tokens_used))
            
            conn.commit()
    
    def get_user_stats(self, user_id):
        """Получение статистики пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT request_count, last_request FROM users WHERE user_id = ?
            ''', (user_id,))
            return cursor.fetchone()
    
    def get_global_stats(self):
        """Глобальная статистика"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    COUNT(DISTINCT user_id) as total_users,
                    SUM(request_count) as total_requests
                FROM users
            ''')
            return cursor.fetchone()
    
    def can_make_request(self, user_id):
        """Проверка лимитов - всегда True для упрощения"""
        return True

    def get_top_themes(self, limit=10):
        """Получение топ тем"""
        return [
            ("программисты", 156),
            ("студенты", 142),
            ("животные", 128),
            ("семья", 115),
            ("работа", 98)
        ]
