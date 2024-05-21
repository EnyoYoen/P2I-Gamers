"""
Affichage de la fênetre de connexion
"""
import tkinter as tk
from tkinter.messagebox import showerror
from password_manager import verify_user

class LoginWin(tk.Tk):

    def __init__(self, queue: list) -> None:
        super().__init__()
        self.queue = queue
<<<<<<< HEAD
        self.user = None
=======
        self.user_id = None
>>>>>>> 8f98c3419b3c3a8051de840bc93a5c6cc3295f6b
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
        user = str(self.username_entry.get())
        password = str(self.password_entry.get())
        
        try:
<<<<<<< HEAD
            good = verify_user(user, password)
=======
            self.user_id = verify_user(str(self.username_entry.get()), str(self.password_entry.get()))
            good = self.user_id is not None
>>>>>>> 8f98c3419b3c3a8051de840bc93a5c6cc3295f6b
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

if __name__ == "__main__":
    win = LoginWin([])
    win.mainloop()
