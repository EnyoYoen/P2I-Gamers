"""
Affichage de la fênetre d'enregistrement
"""
import tkinter as tk


class RegisterWin(tk.Tk):

    def __init__(self, queue) -> None:
        super().__init__()
        self.title('G.M.T. enregistrement')
        self.geometry('300x120')
        self.resizable(width=False, height=False)
        self.creer_widgets()

    def creer_widgets(self) -> None:
        # username
        self.username_label = tk.Label(self, text="Username:")
        self.username_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        self.username_entry = tk.Entry(self)
        self.username_entry.grid(column=1, row=0, sticky=tk.E, padx=5, pady=5)

        # password
        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)

        #confirme password
        self.password_conf_label = tk.Label(self, text="Confirm Password:")
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
        self.login_button = tk.Button(self, text="Connexion")
        self.login_button.grid(column=0, row=3, sticky=tk.E, padx=5, pady=5)
        self.login_button.bind('<Button-1>', self.login)

        # register button
        self.register_button = tk.Button(self, text="Enregistrement")
        self.register_button.grid(column=1, row=3, sticky=tk.W, padx=5, pady=5)
        self.register_button.bind('<Button-1>', self.register_user)


if __name__ == '__main__':
    win = RegisterWin()
    win.mainloop()
