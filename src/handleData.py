import json
from datetime import datetime

FILE_NAME = "users_data.json"

def loadUsersData():
    try:
        with open(FILE_NAME, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def saveUserData(data):
    with open(FILE_NAME, 'w') as file:
        json.dump(data, file, indent=4)

def appendUser(userId, userData):
    if userId not in userData:
        userData[userId] = {}
    userData[userId]['last_played_date'] = ''
    userData[userId]['first_interaction'] = False
    userData[userId]['playing'] = False
    userData[userId]['language'] = 'en'
    userData[userId]['error_count'] = 0
    userData[userId]['gameover'] = False
    userData[userId]['gamewin'] = False
    saveUserData(userData)

def isPlaying(userId, userData):
    today = datetime.now().date().isoformat()
    return userData.get(userId, {}).get('playing', False) and userData.get(userId, {}).get('last_played_date') == today

def startGame(userId, userData):
    today = datetime.now().date().isoformat()
    if userId not in userData:
        userData[userId] = {"first_interaction": True}
    userData[userId]['playing'] = True
    userData[userId]['last_played_date'] = today
    saveUserData(userData)

def stopGame(userId, userData):
    if userId in userData:
        userData[userId]['playing'] = False
        saveUserData(userData)

def changeLanguage(userId, lang, userData):
    if userId not in userData:
        userData[userId] = {"first_interaction": True}
    userData[userId]['language'] = lang
    saveUserData(userData)

def isFirstInteraction(userId, userData):
    return userData.get(userId, {}).get('first_interaction', True)

def playedToday(userId, userData):
    today = datetime.now().date().isoformat()
    return userData.get(userId, {}).get('last_played_date') == today

def incrementErrorCount(userId, userData):
    if userId in userData:
        userData[userId]['error_count'] += 1
        saveUserData(userData)
        return userData[userId]['error_count']
    
def resetErrorCount(userId, userData):
    if userId in userData:
        userData[userId]['error_count'] = 0
        saveUserData(userData)
        return userData[userId]['error_count']

def getErrorCount(userId, userData):
    return userData.get(userId, {}).get('error_count', 0)

def setGameOver(userId, userData):
    if userId in userData:
        userData[userId]['gameover'] = True
        saveUserData(userData)
        return userData[userId]['gameover']
    
def resetGameOver(userId, userData):
    if userId in userData:
        userData[userId]['gameover'] = False
        saveUserData(userData)
        return userData[userId]['gameover']
    
def getGameOver(userId, userData):
    return userData.get(userId, {}).get('gameover', False)

def setGameWin(userId, userData):
    if userId in userData:
        userData[userId]['gamewin'] = True
        saveUserData(userData)
        return userData[userId]['gamewin']

def resetGameWin(userId, userData):
    if userId in userData:
        userData[userId]['gamewin'] = False
        saveUserData(userData)
        return userData[userId]['gamewin']
    
def getGameWin(userId, userData):
    return userData.get(userId, {}).get('gamewin', False)