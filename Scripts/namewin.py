import tkinter as tk

class NameWin(tk.Toplevel) :
	def __init__(self) :
		super().__init__()
		self.title("Nom de la sauvegarde")
		self.attributes("-topmost", True)


		self.label = tk.Label(self, text="Choissisez le nom de la sauvegarde")
		self.label.pack(ipadx=10, ipady=10)

		self.entry_nom = tk.Entry(self)
		self.entry_nom.pack(ipadx=10, ipady=5)

		self.bouton_valider_nom = tk.Button(self, text='Valider')
		self.bouton_valider_nom.bind('<Button-1>', self.confirme_nom)
		self.bouton_valider_nom.pack(ipadx=10, ipady=5)
  
		self.mainloop()

	def confirme_nom(self, event) :
		"Confirme le nom de la sauvegarde"
		self.nom = self.entry_nom.get()
		self.destroy()
		# self.root.indice_historique += 1
		# self.root.list_historique.insert(tk.END, str(self.root.indice_historique) + '- ' + self.nom + ' ' + str(self.root.duree_memo) + 's')
	
if __name__ == '__main__':
	win = NameWin()
	win.mainloop()