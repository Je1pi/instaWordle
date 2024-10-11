import datetime
import sqlite3
import os

# Path to the database
DB_DIR = "src/database/"
DATABASE_NAME = os.path.join(DB_DIR, "wordle.db")

def selectWord(lang):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT word FROM {lang} ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
    except sqlite3.OperationalError:
        raise ValueError("Language table does not exist.")

    conn.close()

    if result:
        return result[0]
    else:
        raise ValueError("No word found for today's date and the specified language.")

def setTodayWord():
    today = datetime.date.today()
    date_str = today.strftime('%Y-%m-%d')

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS words (date TEXT PRIMARY KEY, pt TEXT, en TEXT, es TEXT)")

    cursor.execute("SELECT date FROM words WHERE date = ?", (date_str,))
    result = cursor.fetchone()

    if result:
        conn.close()
        return
    else:
        word_pt = selectWord("pt")
        word_en = selectWord("en")
        word_es = selectWord("es")
        cursor.execute("INSERT INTO words (date, pt, en, es) VALUES (?, ?, ?, ?)", (date_str, word_pt, word_en, word_es))
        conn.commit()
    
    conn.close()

def getTodayWord(lang):
    today = datetime.date.today()
    date_str = today.strftime('%Y-%m-%d')

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT {lang} FROM words WHERE date = ?", (date_str,))
        result = cursor.fetchone()
    except sqlite3.OperationalError:
        raise ValueError("Language table does not exist.")

    conn.close()

    if result:
        return result[0]
    else:
        raise ValueError("No word found for today's date and the specified language.")

def checkWord(user_word, correct_word):
    """Compares the user's word with the correct word and returns emojis."""
    feedback = []
    user = user_word.lower()

    # Check letter by letter
    for i in range(len(user)):
        if user[i] == correct_word[i]:
            feedback.append("🟩")  # Correct letter in the correct position
        elif user[i] in correct_word:
            feedback.append("🟨")  # Correct letter but in the wrong position
        else:
            feedback.append("⬛")  # Letter not in the word

    return ''.join(feedback)

def checkWordCorrect(user_word, correct_word):
    """Checks if the user's word is correct."""
    return user_word.lower() == correct_word.lower()