"""
Affichage de la fênetre de connexion
"""
import tkinter as tk


class LoginWin(tk.Tk):

    def __init__(self, queue) -> None:
        super().__init__()
        self.queue = queue
        self.title('G.M.T. Connexion')
        self.geometry('250x100')
        self.resizable(width=False, height=False)
        self.creer_widgets()
        self.protocol("WM_DELETE_WINDOW", self.quitter)

    def creer_widgets(self) -> None:
        # username
        self.username_label = tk.Label(self, text="Nom d'utilisateur:")
        self.username_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        self.username_entry = tk.Entry(self)
        self.username_entry.grid(column=1, row=0, sticky=tk.E, padx=5, pady=5)

        # password
        self.password_label = tk.Label(self, text="Mot de passe:")
        self.password_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)

        # login button
        self.login_button = tk.Button(self, text="Connexion")
        self.login_button.grid(column=1, row=3, sticky=tk.E, padx=5, pady=5)
        self.login_button.bind('<Button-1>', self.login)

        # register button
        self.register_button = tk.Button(self, text="Enregistrement")
        self.register_button.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)
        self.register_button.bind('<Button-1>', self.register_user)

    def quitter(self):
        self.queue.insert(0, False)
        self.destroy()

    def login(self, event):
        """
        Fonction de connexion
        """
        self.username = str(self.username_entry.get())
        self.password = str(self.password_entry.get())
        #faire requetes sql
        #username , password = recup(self.username, self.password)
        #if username == self.username and password == self.password:
        if True:
            self.queue.insert(0, "connected")
            self.destroy()
            return True

    def register_user(self, event):
        """
        Fonction de création de compte
        """
        self.queue.insert(0, "register")
        self.destroy()

    def recup(self, username: str, password: str):
        pass


if __name__ == "__main__":
    win = LoginWin([])
    win.mainloop()
