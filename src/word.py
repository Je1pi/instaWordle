import datetime
import json

# Load the word list from words.json
with open('src/words.json', 'r') as file:
    WORD_LIST = json.load(file)["words"]  # Acesse a chave "words" diretamente

def get_word_of_the_day():
    """Returns the word of the day based on the current date."""
    # Use the current date to determine the index for the word of the day
    today = datetime.date.today()
    index = today.toordinal() % len(WORD_LIST)  # Ensures the index stays within the list length
    
    # Retorna a palavra do dia
    return WORD_LIST[index]

def check_word_with_emojis(user_word, correct_word):
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

def check_correct_answer(user_word, correct_word):
    """Checks if the user's word is correct."""
    return user_word.lower() == correct_word.lower()