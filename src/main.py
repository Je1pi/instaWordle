from instagrapi import Client # type: ignore
from datetime import datetime
from Command import Commands
from Data import Data
from LogManager import LogManager
import messages
import private
import word
import os

# Users data
usersData = Data()

# Log
log = LogManager()

# Get the 2FA code from user
code = input("2FA Code: ")
log.addToLog("2FA code requested from user")

# Login to Instagram
cl = Client()
cl.login(private.USERNAME, private.PASSWORD, False, code)
log.addToLog("Logged in to Instagram")

# Get user ID of the bot
botID = cl.user_id

# Last Messages
lastMessages = {}

start_time = datetime.now()

# Commands
commands = Commands()

# /Lang command
def langError(client):
    log.addToLog(f"Language command error for user: {client}")
    return messages.TUTO_LANGUAGE[usersData.getLang(client)]

def langCommand(client, lang):
    if lang in ["pt", "en", "es"]:
        log.addToLog(f"Language changed to {lang} for user: {client}")
        usersData.changeLang(client, lang)
        return messages.LANG_CHANGED[usersData.getLang(client)]
    else:
        log.addToLog(f"Invalid language command by user: {client}")
        return messages.INVALID_LANGUAGE[usersData.getLang(client)]

commands.appendCommand("lang", langCommand, langError)

# /Play command
def playCommand(client):
    log.addToLog(f"Game started for user: {client}")
    usersData.setPlaying(client, True)
    return messages.GAME_STARTED[usersData.getLang(client)].format(len(usersData.getWord(client)))

commands.appendCommand("play", playCommand)

# /Stop command
def stopCommand(client):
    log.addToLog(f"Game stopped for user: {client}")
    usersData.setPlaying(client, False)
    return messages.GAME_STOPPED[usersData.getLang(client)]

commands.appendCommand("stop", stopCommand)


print("Bot is running...")
log.addToLog("Bot started")

while True:
    word.setTodayWord()
    log.addToLog("Today's word set")

    threads = cl.direct_threads()
    log.addToLog("Checked direct threads")

    for thread in threads:
        lastMessage = cl.direct_messages(thread.id)[0]

        threadID = thread.id
        message = lastMessage.text
        senderID = lastMessage.user_id
        messageTimestamp = lastMessage.timestamp

        if messageTimestamp < start_time:
            continue

        if senderID == botID:
            continue

        client = thread.users[0].username

        if threadID not in lastMessages or lastMessages[threadID] != message:
            log.addToLog(f"New message from {client}: {message}")
            lastMessages[threadID] = message

            if usersData.isNewUser(client):
                log.addToLog(f"New user: {client} appended to database at {messageTimestamp}")
                usersData.appendUser(client)
                cl.direct_send(messages.WELCOME[usersData.getLang(client)], thread_ids=[threadID])
                continue

            if commands.isCommand(message):
                try:
                    log.addToLog(f"Executing command for user: {client} with message: {message}")
                    response = commands.runCommand(message, client)
                    cl.direct_send(response, thread_ids=[threadID])
                    log.addToLog(f"Command response sent to user: {client}")
                except ValueError as e:
                    log.addToLog(f"Error processing command for user: {client} - {e}")
                    print(e)

            else:
                if usersData.getGameover(client):
                    log.addToLog(f"User {client} tried to play, but game is over")
                    cl.direct_send(messages.ALREADY_PLAYED_TODAY[usersData.getLang(client)], thread_ids=[threadID])

                elif usersData.getGamewin(client):
                    log.addToLog(f"User {client} tried to play, but already won the game")
                    cl.direct_send(messages.ALREADY_PLAYED_TODAY[usersData.getLang(client)], thread_ids=[threadID])

                elif usersData.getPlaying(client):
                    correctWord = usersData.getWord(client)
                    feedback = word.checkWord(message, correctWord)
                    cl.direct_send(feedback, thread_ids=[threadID])
                    log.addToLog(f"Feedback sent to user {client}: {feedback}")

                    if message == usersData.getWord(client):
                        log.addToLog(f"User {client} guessed the correct word")
                        usersData.setGamewin(client)
                        cl.direct_send(messages.CORRECT_GUESS[usersData.getLang(client)], thread_ids=[threadID])

                    else:
                        usersData.appendErrorCount(client)
                        log.addToLog(f"User {client} guessed incorrectly. Error count: {usersData.getErrorCount(client)}")

                        if usersData.getErrorCount(client) > 5:
                            log.addToLog(f"User {client} reached max error count. Game over.")
                            usersData.setGameover(client)
                            cl.direct_send(messages.GAME_OVER[usersData.getLang(client)], thread_ids=[threadID])
                            usersData.setPlaying(client, False)

                        else:
                            cl.direct_send(messages.INCORRECT_GUESS[usersData.getLang(client)].format(usersData.getErrorCount(client)), thread_ids=[threadID])