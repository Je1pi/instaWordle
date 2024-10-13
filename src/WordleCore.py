import datetime
import sqlite3
import os

# Path to the database
DB_DIR = "src/database/"
DATABASE_NAME = os.path.join(DB_DIR, "wordle.db")

class Wordle:
    def __init__(self):
        if not os.path.exists(DATABASE_NAME):
            if not os.path.exists(DB_DIR):
                os.makedirs(DB_DIR)

        self.conn = sqlite3.connect(DATABASE_NAME)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Creates necessary tables in the database if they do not exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dictionary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_pt TEXT NOT NULL,
                word_en TEXT NOT NULL,
                word_es TEXT NOT NULL,
                meaning_pt TEXT,
                meaning_en TEXT,
                meaning_es TEXT,
                difficulty INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                date TEXT PRIMARY KEY,
                pt TEXT,
                en TEXT,
                es TEXT
            )
        ''')
        self.conn.commit()

    def insertWord(self, pt: str, en: str, es: str, meaning_pt=None, meaning_en=None, meaning_es=None, difficulty=0):
        """Inserts a new word with its translations and meanings into the dictionary."""
        if self.isExists(pt):
            return

        self.cursor.execute('''
            INSERT INTO dictionary (word_pt, word_en, word_es, meaning_pt, meaning_en, meaning_es, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (pt, en, es, meaning_pt, meaning_en, meaning_es, difficulty))
        
        self.conn.commit()

    def isExists(self, word: str) -> bool:
        """Checks if a word exists in the dictionary."""
        self.cursor.execute('''
            SELECT 1 FROM dictionary
            WHERE word_pt = ? OR word_en = ? OR word_es = ?
        ''', (word, word, word))
        return self.cursor.fetchone() is not None

    def getRandomWord(self, language, difficulty=0):
        """Gets a random word from the dictionary based on language and difficulty."""
        column_map = {
            "pt": "word_pt",
            "en": "word_en",
            "es": "word_es"
        }
        
        if difficulty:
            self.cursor.execute(f'''
                SELECT {column_map[language]} FROM dictionary
                WHERE difficulty = ?
                ORDER BY RANDOM()
                LIMIT 1
            ''', (difficulty,))
        else:
            self.cursor.execute(f'''
                SELECT {column_map[language]} FROM dictionary
                ORDER BY RANDOM()
                LIMIT 1
            ''')
        
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            raise ValueError("No word found for the specified language and difficulty.")

    def selectWord(self, lang: str) -> str:
        """Selects a random word from a specific language table."""
        column_map = {
            "pt": "pt",
            "en": "en",
            "es": "es"
        }
        
        self.cursor.execute(f"SELECT {column_map[lang]} FROM words ORDER BY RANDOM() LIMIT 1")
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            raise ValueError(f"No word found for the specified language '{lang}'.")

    def setTodayWord(self):
        """Sets the word of the day for each language."""
        today = datetime.date.today()
        date_str = today.strftime('%Y-%m-%d')

        self.cursor.execute("SELECT date FROM words WHERE date = ?", (date_str,))
        result = self.cursor.fetchone()

        if result:
            return
        
        word_pt = self.getRandomWord("pt")
        word_en = self.getRandomWord("en")
        word_es = self.getRandomWord("es")
        self.cursor.execute("INSERT INTO words (date, pt, en, es) VALUES (?, ?, ?, ?)", (date_str, word_pt, word_en, word_es))
        self.conn.commit()

    def getTodayWord(self, lang: str) -> str:
        """Gets the word of the day for the specified language."""
        
        today = datetime.date.today()
        date_str = today.strftime('%Y-%m-%d')

        self.cursor.execute(f"SELECT {lang} FROM words WHERE date = ?", (date_str,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            raise ValueError(f"No word found for today's date and the specified language '{lang}'.")

    def checkWord(self, user: str, correct_word: str, theme: str) -> str:
        """Checks the user's word against the correct word."""
        if len(user) != len(correct_word):
            return None

        feedback = []
        for i in range(len(user)):
            if user[i] == correct_word[i]:
                feedback.append("🟩")
            elif user[i] in correct_word:
                feedback.append("🟨")
            else:
                feedback.append("⬜" if theme == "light" else "⬛")

        return "".join(feedback)

    def checkWordCorrect(self, user_word, correct_word):
        """Checks if the user's word is correct."""
        return user_word.lower() == correct_word.lower()
    
    def getWordMeaning(self, word: str, lang: str) -> str:
        """Gets the meaning of a word in a specific language."""
        column_map = {
            "pt": "meaning_pt",
            "en": "meaning_en",
            "es": "meaning_es"
        }
        
        self.cursor.execute(f"SELECT {column_map[lang]} FROM dictionary WHERE word_{lang} = ?", (word,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            raise ValueError(f"No meaning found for the specified word '{word}' and language '{lang}'.")