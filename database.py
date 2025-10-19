def get_top_themes(self, limit=10):
    """Получение топ тем по популярности"""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute('''
            SELECT theme, COUNT(*) as count 
            FROM requests 
            WHERE theme != 'random' 
            GROUP BY theme 
            ORDER BY count DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

def get_daily_stats(self, date=None):
    """Статистика за конкретный день"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute('''
            SELECT 
                COUNT(*) as total_requests,
                COUNT(DISTINCT user_id) as unique_users
            FROM requests 
            WHERE DATE(created_at) = ?
        ''', (date,))
        return cursor.fetchone()