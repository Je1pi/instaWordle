from LogManager import LogManager
from WordleCore import Wordle
from datetime import datetime
from instagrapi import Client  # type: ignore
from Command import Commands
from Data import Data
import messages
import os


class WordleGame:
    def __init__(self):
        """Inicializa todos os componentes do jogo"""
        # Users data
        self.usersData = Data()

        # Log
        self.log = LogManager()

        # Instagram Client
        self.cl = Client()

        # Bot user ID
        self.botID = None

        # Last messages to prevent repeated processing
        self.lastMessages = {}

        # Start time to filter messages
        self.start_time = datetime.now()

        # Commands
        self.commands = Commands()

        # Wordle Core for game logic
        self.wordle = Wordle()

        # Set up commands
        self._setup_commands()

    def _setup_commands(self):
        """Configura os comandos do bot"""
        # /Lang command
        def langError(client):
            self.log.addToLog(f"Language command error for user: {client}")
            return messages.TUTO_LANGUAGE[self.usersData.getLang(client)]

        def langCommand(client, lang):
            if lang in ["pt", "en", "es"]:
                self.log.addToLog(f"Language changed to {lang} for user: {client}")
                self.usersData.changeLang(client, lang)
                if not self.usersData.getPlaying(client):
                    return messages.LANG_CHANGED[self.usersData.getLang(client)]
                else:
                    return messages.LANG_CHANGED_PLAYING[self.usersData.getLang(client)].format(
                        len(self.usersData.getWord(client))
                    )
            else:
                self.log.addToLog(f"Invalid language command by user: {client}")
                return messages.INVALID_LANGUAGE[self.usersData.getLang(client)]

        self.commands.appendCommand("lang", langCommand, langError)

        # /Play command
        def playCommand(client):
            self.log.addToLog(f"Game started for user: {client}")
            self.usersData.setPlaying(client, True)
            return messages.GAME_STARTED[self.usersData.getLang(client)].format(
                len(self.usersData.getWord(client))
            )

        self.commands.appendCommand("play", playCommand)

        # /Stop command
        def stopCommand(client):
            self.log.addToLog(f"Game stopped for user: {client}")
            self.usersData.setPlaying(client, False)
            return messages.GAME_STOPPED[self.usersData.getLang(client)]

        self.commands.appendCommand("stop", stopCommand)

        # /Theme command
        def themeError(client):
            self.log.addToLog(f"Theme command error for user: {client}")
            return messages.TUTO_THEME[self.usersData.getLang(client)]

        def themeCommand(client, theme):
            if theme in ["dark", "light"]:
                self.log.addToLog(f"Theme changed to {theme} for user: {client}")
                self.usersData.setTheme(client, theme)
                return messages.THEME_CHANGED[self.usersData.getLang(client)]
            else:
                self.log.addToLog(f"Invalid theme command by user: {client}")
                return messages.INVALID_THEME[self.usersData.getLang(client)]

        self.commands.appendCommand("theme", themeCommand, themeError)

        # /Welcome command
        def welcomeCommand(client):
            self.log.addToLog(f"Welcome message sent to user: {client}")
            return messages.WELCOME[self.usersData.getLang(client)]

        self.commands.appendCommand("welcome", welcomeCommand)

        # /tip command
        def tipCommand(client):
            self.log.addToLog(f"Tip sent to user: {client}")
            return self.wordle.getWordMeaning(self.usersData.getWord(client), self.usersData.getLang(client))

        self.commands.appendCommand("tip", tipCommand)

    def login(self, username, password, code2FA):
        """Faz login no Instagram e solicita o código 2FA"""
        self.cl.login(username, password, False, code2FA)
        self.botID = self.cl.user_id
        self.log.addToLog("Logged in to Instagram")

    def exit(self):
        """Realiza logout do Instagram e registra a saída no log"""
        if self.botID is not None:
            self.cl.logout()
            self.log.addToLog("Logged out from Instagram")
        else:
            self.log.addToLog("No active session to log out")

    def update(self):
        """Atualiza o estado do jogo a cada ciclo"""
        self.wordle.setTodayWord()
        self.log.addToLog("Today's word set")

        threads = self.cl.direct_threads()
        self.log.addToLog("Checked direct threads")

        for thread in threads:
            lastMessage = self.cl.direct_messages(thread.id)[0]

            threadID = thread.id
            # Criar um dicionário de usuários para o thread
            users = {user.pk: user.username for user in thread.users if user.pk != self.botID}  # Exclui o bot
            senderID = lastMessage.user_id
            message = (lastMessage.text).lower()
            messageTimestamp = lastMessage.timestamp

            if messageTimestamp < self.start_time:
                continue

            if senderID == self.botID:
                continue

            # Verificar se o ID do remetente está no dicionário de usuários
            sender_username = users.get(senderID)
            if sender_username is None:
                self.log.addToLog(f"Ignored message from bot or unknown user with ID: {senderID}")
                continue

            if threadID not in self.lastMessages or self.lastMessages[threadID] != message:
                self.log.addToLog(f"New message from {sender_username}: {message}")
                self.lastMessages[threadID] = message

                if self.usersData.isNewUser(sender_username):
                    self.log.addToLog(f"New user: {sender_username} appended to database at {messageTimestamp}")
                    self.usersData.appendUser(sender_username)
                    self.cl.direct_send(messages.WELCOME[self.usersData.getLang(sender_username)], thread_ids=[threadID])
                    continue

                if self.commands.isCommand(message):
                    try:
                        self.log.addToLog(f"Executing command for user: {sender_username} with message: {message}")
                        response = self.commands.runCommand(message, sender_username)
                        self.cl.direct_send(response, thread_ids=[threadID])
                        self.log.addToLog(f"Command response sent to user: {sender_username}")
                    except ValueError as e:
                        self.log.addToLog(f"Error processing command for user: {sender_username} - {e}")
                        print(e)
                else:
                    self.handle_gameplay(sender_username, message, threadID)

    def handle_gameplay(self, client, message, threadID):
        """Processa a jogabilidade de adivinhação da palavra"""
        if self.usersData.getGameover(client):
            self.log.addToLog(f"User {client} tried to play, but game is over")
            self.cl.direct_send(messages.ALREADY_PLAYED_TODAY[self.usersData.getLang(client)], thread_ids=[threadID])

        elif self.usersData.getGamewin(client):
            self.log.addToLog(f"User {client} tried to play, but already won the game")
            self.cl.direct_send(messages.ALREADY_PLAYED_TODAY[self.usersData.getLang(client)], thread_ids=[threadID])

        elif self.usersData.getPlaying(client):
            correctWord = self.usersData.getWord(client)
            feedback = self.wordle.checkWord(message, correctWord, self.usersData.getTheme(client))

            if feedback:
                self.cl.direct_send(feedback, thread_ids=[threadID])
                self.log.addToLog(f"Feedback sent to user {client}: {feedback}")

                if self.wordle.checkWordCorrect(message, correctWord):
                    self.log.addToLog(f"User {client} guessed the correct word")
                    self.usersData.setGamewin(client, True)
                    self.cl.direct_send(messages.CORRECT_GUESS[self.usersData.getLang(client)], thread_ids=[threadID])
                    self.usersData.setPlaying(client, False)
                else:
                    self.handle_incorrect_guess(client, threadID)

    def handle_incorrect_guess(self, client, threadID):
        """Processa uma tentativa de adivinhação incorreta"""
        self.usersData.appendErrorCount(client)
        self.log.addToLog(f"User {client} guessed incorrectly. Error count: {self.usersData.getErrorCount(client)}")

        if self.usersData.getErrorCount(client) > 5:
            self.log.addToLog(f"User {client} reached max error count. Game over.")
            self.usersData.setGameover(client, True)
            self.cl.direct_send(messages.GAME_OVER[self.usersData.getLang(client)], thread_ids=[threadID])
            self.usersData.setPlaying(client, False)
        else:
            self.cl.direct_send(
                messages.INCORRECT_GUESS[self.usersData.getLang(client)].format(self.usersData.getErrorCount(client)),
                thread_ids=[threadID],
            )

    def run(self, username, password, code2FA):
        """Inicializa o bot e começa o loop principal"""
        print("Bot is running...")
        self.log.addToLog("Bot started")
        self.login(username, password, code2FA)