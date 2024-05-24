"""
Affichage de la fênetre d'enregistrement
"""
import tkinter as tk
from tkinter.messagebox import showerror, showwarning, showinfo
from password_manager import register_user

class RegisterWin(tk.Tk):

    def __init__(self, queue) -> None:
        super().__init__()
        self.queue = queue
        self.user_id = None
        self.title('G.M.T. Enregistrement')
        #self.geometry('320x160')
        #self.resizable(width=False, height=False)
        self.creer_widgets()
        self.protocol("WM_DELETE_WINDOW", self.quitter)

    def creer_widgets(self) -> None:
        # username
        self.username_label = tk.Label(self, text="Nom d'utilisateur:")
        self.username_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        self.username_entry = tk.Entry(self)
        self.username_entry.grid(column=1, row=0, sticky=tk.E, padx=5, pady=5)

        #height
        self.height_label = tk.Label(self, text="Taille de l'utilisateur")
        self.height_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        self.height_entry = tk.Entry(self)
        self.height_entry.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)


        # password
        self.password_label = tk.Label(self, text="Mot de passe:")
        self.password_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(column=1, row=2, sticky=tk.E, padx=5, pady=5)

        #confirm password
        self.password_conf_label = tk.Label(self, text="Confirmation mot de passe:")
        self.password_conf_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)

        self.password_conf_entry = tk.Entry(self, show="*")

        self.password_conf_entry.grid(column=1, row=3, sticky=tk.E, padx=5, pady=5)

        #Is it a teacher
        self.is_a_teacher_label = tk.Label(self, text="Mode enseignant :")
        self.is_a_teacher_label.grid(column=0, row=4, sticky=tk.E, padx=5, pady=5)

        self.is_teacher = tk.IntVar()
        self.is_a_teacher_checkbutton = tk.Checkbutton(self, variable=self.is_teacher, onvalue=True, offvalue=False)
        self.is_a_teacher_checkbutton.grid(column=1, row=4, sticky=tk.W, padx=5, pady=5)    

        # login button
        self.login_button = tk.Button(self, text="Retour connexion")
        self.login_button.bind('<Button-1>', self.login)
        self.login_button.grid(column=0, row=5, sticky=tk.E, padx=5, pady=5)

        # register button
        self.register_button = tk.Button(self, text="Enregistrement")
        self.register_button.bind('<Button-1>', self.register_the_user)
        self.register_button.grid(column=1, row=5, sticky=tk.W, padx=5, pady=5)


    def get_height(self) -> int:
        d = self.height_entry.get()
        try:
            return int(d)
        except ValueError:
            if d == '':
                return 0
            else:
                return
        
    def register_the_user(self, event):

        user = self.username_entry.get()
        height = self.get_height()
        password = self.password_entry.get()
        password_conf = self.password_conf_entry.get()
        is_teacher = bool(self.is_teacher.get())

        if not user:
            showwarning(title='Attention', message="Il faut un nom d'utilisateur")
        elif not height:
            showwarning(title='Attention', message="La taille doit entre cm")
        elif height == 0:
            showwarning(title='Attention', message="Il faut remplir la taille")
        elif not password:
            showwarning(title='Attention', message='Le mot de passe ne peut pas être vide ')
        elif not password_conf:
            showwarning(title='Attention', message="Il faut remplir la confirmation de mot de passe")
        elif password_conf != password:
            showerror(title='Erreur', message='Les mots de passes ne correspondent pas')
        else:

            user_id = register_user(user, password, height, is_teacher)
            if user_id:
                showinfo(title='Information', message=f'Le compte a été créé \n Bienvenue {user} !')
                self.queue[0]='connected'
                self.user_id = user_id
                self.destroy()
            else:
                showerror(title='Erreur', message="Le nom d'utilisateur est déjà utilisé")
            

    def login(self, event):
        self.destroy()

    def quitter(self):
        self.destroy()
        self.queue[0] = True


if __name__ == '__main__':
    win = RegisterWin(['register'])
    win.mainloop()
