from WordleCore import Wordle
from datetime import datetime
import sqlite3
import os

# Path to the database
DB_DIR = "src/database/"
DATABASE_NAME = os.path.join(DB_DIR, "users.db")

class Data:
    def __init__(self):
        self.wordle = Wordle()
        self.createDatabaseIfNotExists()

    def createDatabaseIfNotExists(self):
        if not os.path.exists(DATABASE_NAME):
            if not os.path.exists(DB_DIR):
                os.makedirs(DB_DIR)

            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                last_played_date TEXT,
                playing BOOLEAN DEFAULT 0,
                language TEXT DEFAULT 'en',
                error_count INTEGER DEFAULT 0,
                gameover BOOLEAN DEFAULT 0,
                gamewin BOOLEAN DEFAULT 0,
                word TEXT DEFAULT '',
                theme TEXT DEFAULT 'dark',
                difficulty INTEGER DEFAULT 1,
                chances INTEGER DEFAULT 5
            );
            ''')

            conn.commit()
            conn.close()

    def getUsers(self):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    
    def getUser(self, user_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def appendUser(self, userID):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (user_id, last_played_date) VALUES (?, ?)", (userID, datetime.now()))
        conn.commit()
        conn.close()

    def setWord(self, user_id, lang):
        if self.getPlaying(user_id):
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            word = self.wordle.getTodayWord(lang)
            difficulty = self.getDifficulty(user_id)

            chances = max(5, 5 + difficulty)

            cursor.execute("UPDATE users SET word = ?, chances = ? WHERE user_id = ?", (word, chances, user_id))
            conn.commit()
            conn.close()

    def getWord(self, user_id):
        if self.getPlaying(user_id):
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT word FROM users WHERE user_id = ?", (user_id,))
            word = cursor.fetchone()
            conn.close()
            return word[0] if word else None

    def getLang(self, user_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        lang = cursor.fetchone()
        conn.close()
        return lang[0] if lang else 'en'
    
    def changeLang(self, user_id, lang):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
        conn.commit()
        conn.close()
        self.setWord(user_id, lang)

    def getPlaying(self, user_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT playing FROM users WHERE user_id = ?", (user_id,))
        playing = cursor.fetchone()
        conn.close()
        return playing[0] if playing else 0
    
    def setPlaying(self, user_id, playing):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET playing = ? WHERE user_id = ?", (1 if playing else 0, user_id))
        conn.commit()
        conn.close()
        self.setWord(user_id, self.getLang(user_id))
    
    def getErrorCount(self, user_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT error_count FROM users WHERE user_id = ?", (user_id,))
        error_count = cursor.fetchone()
        conn.close()
        return error_count[0] if error_count else 0
    
    def appendErrorCount(self, user_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET error_count = error_count + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def resetErrorCount(self, user_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET error_count = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def getGameover(self, user_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT gameover FROM users WHERE user_id = ?", (user_id,))
        gameover = cursor.fetchone()
        conn.close()
        return gameover[0] if gameover else 0
    
    def setGameover(self, user_id, gameover):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET gameover = ? WHERE user_id = ?", (1 if gameover else 0, user_id))
        conn.commit()
        conn.close()
    
    def resetGameover(self, user_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET gameover = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def getGamewin(self, user_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT gamewin FROM users WHERE user_id = ?", (user_id,))
        gamewin = cursor.fetchone()
        conn.close()
        return gamewin[0] if gamewin else 0
    
    def setGamewin(self, user_id, gamewin):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET gamewin = ? WHERE user_id = ?", (1 if gamewin else 0, user_id))
        conn.commit()
        conn.close()
    
    def resetGamewin(self, user_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET gamewin = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    def setTheme(self, user_id, theme):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET theme = ? WHERE user_id = ?", (theme, user_id))
        conn.commit()
        conn.close()
    
    def getTheme(self, user_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT theme FROM users WHERE user_id = ?", (user_id,))
        theme = cursor.fetchone()
        conn.close()
        return theme[0] if theme else 'black'

    def isNewUser(self, user_id):
        return not self.getUser(user_id)
    
    def getDifficulty(self, user_id):
        """Obtém a dificuldade do usuário."""
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT difficulty FROM users WHERE user_id = ?", (user_id,))
        difficulty = cursor.fetchone()
        conn.close()
        return difficulty[0] if difficulty else -1