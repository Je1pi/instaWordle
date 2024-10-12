from instagrapi import Client # type: ignore
from datetime import datetime
from Command import Commands
from Data import Data
import messages
import private
import word
import os

# Users data
usersData = Data()

# Get the 2FA code from user
code = input("2FA Code: ")

# Login to Instagram
cl = Client()
cl.login(private.USERNAME, private.PASSWORD, False, code)

# Get user ID of the bot
botID = cl.user_id

# Last Messages
lastMessages = {}

start_time = datetime.now()

# Commands
commands = Commands()

# /Lang command
def langError(client):
    return messages.TUTO_LANGUAGE[usersData.getLang(client)]

def langCommand(client, lang):
    if lang in ["pt", "en", "es"]:
        usersData.changeLang(client, lang)
        return messages.LANG_CHANGED[usersData.getLang(client)]
    else:
        return messages.INVALID_LANGUAGE[usersData.getLang(client)]

commands.appendCommand("lang", langCommand, langError)

# /Play command
def playCommand(client):
    usersData.setPlaying(client, True)
    usersData.setWord(client, usersData.getLang(client))
    return messages.GAME_STARTED[usersData.getLang(client)]

commands.appendCommand("play", playCommand)

# /Stop command
def stopCommand(client):
    usersData.setPlaying(client, False)
    return messages.GAME_STOPPED[usersData.getLang(client)]

commands.appendCommand("stop", stopCommand)


print("Bot is running...")
while True:
    word.setTodayWord()

    threads = cl.direct_threads()

    for thread in threads:
        lastMessage = cl.direct_messages(thread.id)[0]

        threadID = thread.id
        message = lastMessage.text
        senderID = lastMessage.user_id
        messageTimestamp = lastMessage.timestamp

        if messageTimestamp < start_time:
            continue

        if senderID != botID:
            client = thread.users[0].username

            if threadID not in lastMessages or lastMessages[threadID] != message:
                print(f"New message from {client}: {message}")            
                lastMessages[threadID] = message

                if usersData.isNewUser(client):
                    print(f"New user: {client} appended to database at {messageTimestamp}")
                    usersData.appendUser(client)
                    cl.direct_send(messages.WELCOME[usersData.getLang(client)], thread_ids=[threadID])
                    continue

                if commands.isCommand(message):
                    try:
                        response = commands.runCommand(message, client)
                        cl.direct_send(response[usersData.getLang(client)], thread_ids=[threadID])
                    except ValueError as e:
                        print(e)
                
                else:
                    if usersData.getGameover(client):
                        cl.direct_send(messages.ALREADY_PLAYED_TODAY[usersData.getLang(client)], thread_ids=[threadID])
                    
                    elif usersData.getGamewin(client):
                        cl.direct_send(messages.ALREADY_PLAYED_TODAY[usersData.getLang(client)], thread_ids=[threadID])
                    
                    elif usersData.getPlaying(client):
                        correctWord = usersData.getWord(client)
                        feedback = word.checkWord(message, correctWord)
                        cl.direct_send(feedback, thread_ids=[threadID])
                        
                        if message == correctWord:
                            usersData.setGamewin(client)
                            cl.direct_send(messages.CORRECT_GUESS[usersData.getLang(client)], thread_ids=[threadID])
                        
                        else:
                            usersData.appendErrorCount(client)

                            if usersData.getErrorCount(client) > 5:
                                usersData.setGameover(client)
                                cl.direct_send(messages.GAME_OVER[usersData.getLang(client)], thread_ids=[threadID])
                                usersData.setPlaying(client, False)
                            
                            else:
                                cl.direct_send(messages.INCORRECT_GUESS[usersData.getLang(client)].format(usersData.getErrorCount(client)), thread_ids=[threadID])