import tkinter as tk
from namewin import nameWin
from tkinter import messagebox

class demandeSauvegarde(tk.Tk) :
  def __init__(self, root) :
    super().__init__()
    self.title("Sauvegarde")
    self.root = root
    self.label_demande = tk.Label(self, text="Souhaitez-vous sauvegarder votre enregistrement ?")
    self.label_demande.pack()

    self.choix = tk.StringVar()
    self.choix.set("non")
    
    self.bouton_oui = tk.Button(self, text='oui')
    self.bouton_oui.bind('<Button-1>', self.execute_oui)
    self.bouton_oui.pack()

    self.bouton_non = tk.Button(self, text='non')
    self.bouton_non.bind('<Button-1>', self.execute_non)
    self.bouton_non.pack()
  
  def execute_oui(self, event) :
    "Execute le choix de l'utilisateur"
    #nameWin(self)
    self.destroy()
    messagebox.showinfo("nom")
      
  def execute_non(self, event) :
      self.destroy()

