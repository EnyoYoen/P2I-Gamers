"""
Affichage de la fênetre de connexion
"""
import tkinter as tk
from tkinter.messagebox import showerror
from password_manager import PasswordManager

class LoginWin(tk.Tk, PasswordManager):

    def __init__(self, queue: list) -> None:
        super().__init__()
        PasswordManager.__init__(self)
        self.queue = queue
        self.user_id = None
        self.title('G.M.T. Connexion')
        # self.geometry('250x100')
        # self.resizable(width=False, height=False)
        self.creer_widgets()
        self.protocol("WM_DELETE_WINDOW", self.quitter)

    def creer_widgets(self) -> None:
        # username
        self.username_label = tk.Label(self, text="Nom d'utilisateur:")
        self.username_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        self.username_entry = tk.Entry(self)
        self.username_entry.grid(column=1, row=0, sticky=tk.E, padx=5, pady=5)
        self.username_entry.focus_set()
        self.username_entry.bind('<Return>', self.return_username)

        # password
        self.password_label = tk.Label(self, text="Mot de passe:")
        self.password_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)
        self.password_entry.bind('<Return>', self.return_password)

        # login button
        self.login_button = tk.Button(self, text="Connexion")
        self.login_button.bind('<Button-1>', self.login)
        self.login_button.grid(column=1, row=3, sticky=tk.E, padx=5, pady=5)
 
        # register button
        self.register_button = tk.Button(self, text="Enregistrement")
        self.register_button.bind('<Button-1>', self.register_user)
        self.register_button.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)

    def quitter(self)-> None:
        self.queue.insert(0, False)
        self.destroy()

    def login(self, event) -> None:
        """
        Fonction de connexion
        """
        user = str(self.username_entry.get()).strip()
        password = str(self.password_entry.get()).strip()
        
        try:
            self.user_id = self.verify_user(user, password)
            good = self.user_id is not None
        except:
            good = False
        
        if good:
            self.queue.insert(0, "connected")
            self.user = user 
            self.destroy()
        else:
            showerror(title='Erreur', message="L'utilisateur et le mot passe ne correspondent pas.")

    def register_user(self, event)-> None:
        """
        Fonction de création de compte
        """
        self.queue.insert(0, "register")
        self.destroy()

    def return_username(self, event) :
        self.password_entry.focus_set()

    def return_password(self, event) :
        self.login('<Return>')

if __name__ == "__main__":
    win = LoginWin([])
    win.mainloop()
