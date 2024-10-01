from instagrapi import Client
import handleData
import messages
import private
import time
import word

# Get the 2FA code from user
code = input("2FA Code: ")

# Login to Instagram
cl = Client()
cl.login(private.USERNAME, private.PASSWORD, False, code)

# Get user ID of the bot
bot_user_id = cl.user_id_from_username(private.USERNAME)

# Dictionary to store last message from each client
last_messages = {}

# Load user data
users_data = handleData.loadUsersData()

# Get the word of the day
word_of_the_day = word.get_word_of_the_day()

# Store the timestamp of the first execution
start_time = time.time()

# Main loop
print("Checking for new messages...")
while True:
    threads = cl.direct_threads()

    for thread in threads:
        last_message_in_thread = cl.direct_messages(thread.id)[0]

        thread_id = thread.id
        message_text = last_message_in_thread.text
        sender_id = last_message_in_thread.user_id
        message_timestamp = last_message_in_thread.created_at.timestamp()

        # Ignore messages received before the bot started
        if message_timestamp < start_time:
            continue

        # Get the username of the client
        if sender_id != bot_user_id:
            client = thread.users[0].username

            if thread_id not in last_messages or last_messages[thread_id] != message_text:
                print(f"New message from {client}: {message_text}")
                last_messages[thread_id] = message_text

                # Check if the first interaction
                if handleData.isFirstInteraction(sender_id, users_data):
                    cl.direct_send(messages.welcome[users_data.get(sender_id, {}).get('language', 'en')], thread_ids=[thread_id])
                    handleData.appendUser(sender_id, users_data)
                    continue

                if message_text == "/play" or message_text == "/start":
                    if not handleData.playedToday(sender_id, users_data) and not handleData.isPlaying(sender_id, users_data):
                        handleData.startGame(sender_id, users_data)
                        cl.direct_send(messages.game_started[users_data.get(sender_id, {}).get('language', 'en')], thread_ids=[thread_id])
                    else:
                        cl.direct_send(messages.already_played_today[users_data.get(sender_id, {}).get('language', 'en')], thread_ids=[thread_id])
                
                elif message_text == "/stop":
                    handleData.stopGame(sender_id, users_data)
                    cl.direct_send(messages.game_stopped[users_data.get(sender_id, {}).get('language', 'en')], thread_ids=[thread_id])
                
                elif message_text.startswith("/lang"):
                    lang = message_text.split(" ")[1]
                    handleData.changeLanguage(sender_id, lang, users_data)
                    cl.direct_send(messages.language[lang], thread_ids=[thread_id])
                    cl.direct_send(messages.welcome[lang], thread_ids=[thread_id])
                
                elif handleData.getGameWin(sender_id, users_data):
                    cl.direct_send(messages.game_winded[users_data.get(sender_id, {}).get('language', 'en')], thread_ids=[thread_id])

                elif handleData.getGameOver(sender_id, users_data):
                    cl.direct_send(messages.already_played_today[users_data.get(sender_id, {}).get('language', 'en')], thread_ids=[thread_id])

                else:
                    if handleData.isPlaying(sender_id, users_data) and not handleData.getGameOver(sender_id, users_data):
                        message_lower = message_text.lower()
                        
                        if len(message_lower) != len(word_of_the_day):
                            lang = users_data.get(sender_id, {}).get('language', 'en')
                            invalid_length_message = messages.invalid_guess_length[lang].format(len(word_of_the_day))
                            cl.direct_send(invalid_length_message, thread_ids=[thread_id])
                            continue

                        if message_lower == word_of_the_day:
                            handleData.stopGame(sender_id, users_data)
                            handleData.setGameWin(sender_id, users_data)
                            cl.direct_send(messages.correct_guess[users_data.get(sender_id, {}).get('language', 'en')], thread_ids=[thread_id])
                        
                        elif not handleData.getGameOver(sender_id, users_data):
                            handleData.incrementErrorCount(sender_id, users_data)
                            lang = users_data.get(sender_id, {}).get('language', 'en')
                            cl.direct_send(word.check_word_with_emojis(message_lower, word_of_the_day), thread_ids=[thread_id])
                            if handleData.getErrorCount(sender_id, users_data) >= 6:
                                handleData.setGameOver(sender_id, users_data)
                                cl.direct_send(messages.game_over[lang], thread_ids=[thread_id])
                            else:
                                incorrect_guess_message = messages.incorrect_guess[lang].format(handleData.getErrorCount(sender_id, users_data))
                                cl.direct_send(incorrect_guess_message, thread_ids=[thread_id])

    time.sleep(0.1)