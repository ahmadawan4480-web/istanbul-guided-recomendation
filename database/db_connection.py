import sqlite3
import os
from datetime import datetime

class DatabaseConnection:
    def __init__(self, db_path="database/istanbul_recommendations.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                interests TEXT,  -- JSON string of interests list
                created_date TEXT,
                updated_date TEXT
            )
        ''')

        # Ratings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                place_name TEXT,
                rating REAL,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Visited places table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visited_places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                place_name TEXT,
                visit_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Cache table for LLM responses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE,
                response TEXT,
                created_at REAL,
                ttl INTEGER
            )
        ''')

        conn.commit()
        conn.close()

    def create_user(self, user_id, name, interests=None):
        """Create a new user profile"""
        if interests is None:
            interests = []
        interests_str = ','.join(interests)
        now = datetime.now().isoformat()

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, name, interests, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, name, interests_str, now, now))
        conn.commit()
        conn.close()

    def get_user(self, user_id):
        """Get user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id, name, interests_str, created, updated = user
            interests = interests_str.split(',') if interests_str else []
            return {
                'user_id': user_id,
                'name': name,
                'interests': interests,
                'created_date': created,
                'updated_date': updated
            }
        return None

    def update_user_interests(self, user_id, interests):
        """Update user interests"""
        interests_str = ','.join(interests)
        now = datetime.now().isoformat()

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET interests = ?, updated_date = ? WHERE user_id = ?
        ''', (interests_str, now, user_id))
        conn.commit()
        conn.close()

    def add_rating(self, user_id, place_name, rating):
        """Add or update a rating for a place"""
        now = datetime.now().isoformat()

        conn = self.get_connection()
        cursor = conn.cursor()
        # Check if rating exists
        cursor.execute('''
            SELECT id FROM ratings WHERE user_id = ? AND place_name = ?
        ''', (user_id, place_name))

        existing = cursor.fetchone()
        if existing:
            cursor.execute('''
                UPDATE ratings SET rating = ?, timestamp = ? WHERE id = ?
            ''', (rating, now, existing[0]))
        else:
            cursor.execute('''
                INSERT INTO ratings (user_id, place_name, rating, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, place_name, rating, now))
        conn.commit()
        conn.close()

    def get_user_ratings(self, user_id):
        """Get all ratings for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT place_name, rating, timestamp FROM ratings WHERE user_id = ?', (user_id,))
        ratings = cursor.fetchall()
        conn.close()

        return [{'place_name': r[0], 'rating': r[1], 'timestamp': r[2]} for r in ratings]

    def get_place_average_rating(self, place_name):
        """Get average rating for a place"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT AVG(rating) FROM ratings WHERE place_name = ?', (place_name,))
        avg = cursor.fetchone()[0]
        conn.close()
        return avg if avg else 0.0

    def add_visited_place(self, user_id, place_name):
        """Mark a place as visited"""
        now = datetime.now().isoformat()

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO visited_places (user_id, place_name, visit_date)
            VALUES (?, ?, ?)
        ''', (user_id, place_name, now))
        conn.commit()
        conn.close()

    def get_visited_places(self, user_id):
        """Get visited places for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT place_name, visit_date FROM visited_places WHERE user_id = ?', (user_id,))
        visited = cursor.fetchall()
        conn.close()

        return [{'place_name': v[0], 'visit_date': v[1]} for v in visited]

    def cache_llm_response(self, cache_key, response, ttl=3600):
        """Cache LLM response"""
        import time
        now = time.time()

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO llm_cache (cache_key, response, created_at, ttl)
            VALUES (?, ?, ?, ?)
        ''', (cache_key, response, now, ttl))
        conn.commit()
        conn.close()

    def get_cached_llm_response(self, cache_key):
        """Get cached LLM response if not expired"""
        import time
        now = time.time()

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT response, created_at, ttl FROM llm_cache WHERE cache_key = ?
        ''', (cache_key,))
        result = cursor.fetchone()
        conn.close()

        if result:
            response, created_at, ttl = result
            if now - created_at < ttl:
                return response
        return None

    def clear_expired_cache(self):
        """Clear expired cache entries"""
        import time
        now = time.time()

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM llm_cache WHERE (? - created_at) > ttl', (now,))
        conn.commit()
        conn.close()