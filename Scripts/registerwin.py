"""
Affichage de la fênetre d'enregistrement
"""
import tkinter as tk
from tkinter.messagebox import showerror, showwarning, showinfo


class RegisterWin(tk.Tk):

    def __init__(self, queue) -> None:
        super().__init__()
        self.queue = queue
        self.title('G.M.T. Enregistrement')
        self.geometry('320x130')
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

        #confirme password
        self.password_conf_label = tk.Label(self, text="Confirmation mot de passe:")
        self.password_conf_label.grid(column=0,
                                      row=2,
                                      sticky=tk.W,
                                      padx=5,
                                      pady=5)

        self.password_conf_entry = tk.Entry(self, show="*")

        self.password_conf_entry.grid(column=1,
                                      row=2,
                                      sticky=tk.E,
                                      padx=5,
                                      pady=5)

        # login button
        self.login_button = tk.Button(self, text="Retour connexion")
        self.login_button.grid(column=0, row=3, sticky=tk.E, padx=5, pady=5)
        self.login_button.bind('<Button-1>', self.login)

        # register button
        self.register_button = tk.Button(self, text="Enregistrement")
        self.register_button.grid(column=1, row=3, sticky=tk.W, padx=5, pady=5)
        self.register_button.bind('<Button-1>', self.register_user)

    def register_user(self, event):
        if not self.username_entry.get():
            showwarning(title='Attention', message="Il faut un nom d'utilisateur")
        elif not self.password_entry.get():
            showerror(title='Erreur', message='Le mot de passe ne peut pas être vide ')
        elif not self.password_conf_entry.get():
            showwarning(title='Attention', message="Il faut remplir la confirmation de mot de passe")

        elif self.password_conf_entry.get() != self.password_entry.get():
            showerror(title='Erreur', message='Les mots de passes ne correspondent pas')
        else:
            showinfo(title='Information', message=f'Le compte a été créé \n Bienvenu {self.username_entry.get()} !')
            ... #Metre dans la base de donnée
            self.queue[0]='connected'
            self.destroy()
            

    def login(self, event):
        self.destroy()

    def quitter(self):
        self.destroy()
        self.queue[0] = True


if __name__ == '__main__':
    win = RegisterWin(['register'])
    win.mainloop()
