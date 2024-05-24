import tkinter as tk

class NameWin(tk.Toplevel) :
	def __init__(self) :
		super().__init__()
		self.title("Nom de la sauvegarde")
		self.entry_nom = tk.Entry(self)
		self.entry_nom.pack()
		self.bouton_valider_nom = tk.Button(self, text='valider')
		self.bouton_valider_nom.bind('<Button-1>', self.confirme_nom)
		self.bouton_valider_nom.pack()
  
		self.mainloop()

	def confirme_nom(self, event) :
		"Confirme le nom de la sauvegarde"
		self.nom = self.entry_nom.get()
		self.destroy()
		# self.root.indice_historique += 1
		# self.root.list_historique.insert(tk.END, str(self.root.indice_historique) + '- ' + self.nom + ' ' + str(self.root.duree_memo) + 's')
		