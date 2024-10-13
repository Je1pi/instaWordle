import os
import sys

sys.path.append(os.path.abspath("src"))

from src.Game import WordleGame as wg
from src.Interface import LoginWindow
import tkinter as tk

def start_game(username, password, code):
    app = wg()
    app.run(username, password, code)

    while True:
        app.update()

if __name__ == "__main__":
    root = tk.Tk()
    
    def on_login(username, password, code):
        start_game(username, password, code)

    login_window = LoginWindow(root, on_login, credentials_file='credentials.json')
    
    root.mainloop()
