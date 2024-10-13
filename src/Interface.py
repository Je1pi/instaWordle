import tkinter as tk
from tkinter import messagebox
import json

class LoginWindow:
    """
    A class to create a login window for Instagram authentication.

    Attributes:
        root (tk.Tk): The main Tkinter window.
        on_login (function): A callback function to call upon successful login.
        credentials_file (str): The name of the JSON file containing credentials.
    """
    
    def __init__(self, root: tk.Tk, on_login: callable, credentials_file: str = 'credentials.json'):
        """
        Initializes the LoginWindow with the provided parameters.

        Args:
            root (tk.Tk): The main Tkinter window.
            on_login (callable): A callback function to call upon successful login.
            credentials_file (str): The name of the JSON file containing credentials (default is 'credentials.json').
        """
        self.root = root
        self.root.title("Instagram Login")
        self.on_login = on_login  # Function to call on successful login
        self.credentials_file = credentials_file  # Name of the credentials file
        
        # Username field
        self.username_label = tk.Label(root, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()
        
        # Checkbox for username from JSON
        self.use_private_username = tk.BooleanVar()
        self.username_checkbox = tk.Checkbutton(root, text="Use username from credentials.json", variable=self.use_private_username)
        self.username_checkbox.pack()
        
        # Password field
        self.password_label = tk.Label(root, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()
        
        # Checkbox for password from JSON
        self.use_private_password = tk.BooleanVar()
        self.password_checkbox = tk.Checkbutton(root, text="Use password from credentials.json", variable=self.use_private_password)
        self.password_checkbox.pack()
        
        # 2FA code field
        self.code_label = tk.Label(root, text="2FA Code")
        self.code_label.pack()
        self.code_entry = tk.Entry(root)
        self.code_entry.pack()
        
        # Login button
        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack()

    def load_credentials(self) -> dict:
        """
        Loads credentials from the specified JSON file.

        Returns:
            dict: A dictionary containing the username and password, or None if there was an error.
        """
        try:
            with open(self.credentials_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "Credentials not found. Please create a credentials.json file.")
            return None
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error decoding JSON. Please check the format.")
            return None

    def login(self):
        """
        Handles the login process. Validates input fields and calls the on_login function
        with the provided username, password, and 2FA code.
        """
        # Load credentials from the JSON file if the checkboxes are selected
        credentials = self.load_credentials() if self.use_private_username.get() or self.use_private_password.get() else None
        
        # Get username and password
        username = credentials.get('username') if self.use_private_username.get() and credentials else self.username_entry.get()
        password = credentials.get('password') if self.use_private_password.get() and credentials else self.password_entry.get()
        code = self.code_entry.get()

        if not username or not password or not code:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Call the on_login function with the provided credentials
        self.on_login(username, password, code)

        # Close the window
        self.root.destroy()