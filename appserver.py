import os
import sys

sys.path.append(os.path.abspath("src"))

from src.Game import WordleGame as wg
import json

def load_credentials(filename='credentials.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Credenciais não encontradas. Por favor, crie um arquivo credentials.json.")
        return None
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON. Verifique o formato.")
        return None

def main():
    credentials = load_credentials()

    if credentials is None:
        return

    username = input("Digite seu username: ") or credentials.get('username')
    password = input("Digite sua senha: ") or credentials.get('password')
    code = input("Digite seu código 2FA: ")

    if not username or not password or not code:
        print("Todos os campos são obrigatórios!")
        return

    app.run(username, password, code)

    while True:
        app.update()

if __name__ == "__main__":
    app = wg()

    try:
        main()
    except KeyboardInterrupt:
        app.exit()