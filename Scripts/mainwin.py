'''
Affichage de la Fenêtre Principale
'''
import tkinter as tk
import time
from namewin import nameWin
from tkinter import messagebox
from dataclass import *
from database import db
import comparaison as cp
from server import DataServer

mvt_exp = MesureVect.from_raw_list([(0,0,1,2,3,1),(1,1,4,5,6,2),(2,2,7,8,9,3)])
data_th = {"aurevoir":MesureVect.from_raw_list([(0,3,10,9,8,1),(0,4,7,6,5,1.5),(0,5,4,3,2,2),(0,6,1,1,1,2.6),(0,7,1,2,3,3)]),
					 "coucou":MesureVect.from_raw_list([(0,13,1,2,3,1),(0,12,4,5,6,1.5),(0,11,7,8,9,2),(0,10,1,1,1,2.6),(0,9,1,2,3,3),(0,8,0,0,0,4)])}

class MainWin(tk.Tk, DataServer):
	def __init__(self,user_id):
		super().__init__()
		DataServer.__init__(self)
		self.user_id = user_id

		self.title('G.M.T.')
		#self.geometry('500x800')
		self.creer_widgets()

	def creer_widgets(self):
		"""
		Création des widgets
		"""
		#Label toute en haut
		self.label = tk.Label(self, text="Hello World")
		self.label.grid(column=3,row=0)

		#Frame historique
		self.frame_historique = tk.Frame(self)
		self.frame_historique.columnconfigure(0, weight = 1)
		self.frame_historique.rowconfigure(0, weight=1)
		
		#Scrollbar a droite de la liste pour l'historique
		self.scrollbar = tk.Scrollbar(self.frame_historique)
		self.scrollbar.grid(column=1,row=0, sticky='nesw')

		#Liste historique
		self.list_historique = tk.Listbox(self.frame_historique, yscrollcommand=self.scrollbar.set)
		self.list_historique.grid(column=0,row=0, sticky='nesw')
		
		for i in range(50):
			self.list_historique.insert(tk.END, str(i) + ' - historique') #A modifier
		
		self.scrollbar.config(command = self.list_historique.yview )

		#Frame pré-enregistrement
		self.frame_pre_enregistrement = tk.Frame(self)

		#Scrollbar a droite de la liste pour le pré-enregistrement
		self.scrollbar_pre_enregistrement = tk.Scrollbar(self.frame_pre_enregistrement)
		self.scrollbar_pre_enregistrement.grid(column=1,row=0, sticky='nesw')

		#Liste pré enregistrement
		self.list_pre_enregistrement = tk.Listbox(self.frame_pre_enregistrement, yscrollcommand=self.scrollbar_pre_enregistrement.set)
		self.list_pre_enregistrement.grid(column=0,row=0, sticky='nesw')

		for i in range(50):
			self.list_pre_enregistrement.insert(tk.END, str(i) + ' - pre enregistrement') #A modifier

		self.scrollbar_pre_enregistrement.config(command = self.list_pre_enregistrement.yview )

		#Afficher la frame pré-enregistrement
		self.frame_pre_enregistrement.grid(column=0, columnspan= 3,row=2,rowspan = 9,sticky='nesw')
		self.frame_pre_enregistrement.columnconfigure(0, weight = 1)
		self.frame_pre_enregistrement.rowconfigure(0, weight=1)
		
		#Bouton historique
		self.button_historique = tk.Button(self, text="ᅠHistoriqueᅠ")
		self.button_historique.bind('<Button-1>', self.afficher_historique)
		self.button_historique.grid(column=1,row=1, sticky="nesw")
		

		#Bouton pré-enregistrement
		self.button_preenregistrement = tk.Button(self, text="Pré-enregistre")
		self.button_preenregistrement.bind('<Button-1>', self.afficher_preenregistrement)
		self.button_preenregistrement.grid(column=0,row=1, sticky='nesw')
		
		#cadre visualisation
		self.canevas = tk.Canvas(self, background='lightblue') #width=400, height=500
		self.canevas.grid(column=3,columnspan=6,row=1,rowspan= 10, sticky='nesw')
		
		#gestion enregistrement
		self.duree = 0
		self.running = False
		self.chrono = tk.Label(text='00:00:00')
		self.chrono.grid(row=13, column=3)

		self.label_enregistrement = tk.Label(text="Commencer l'enregistrement")
		self.label_enregistrement.grid(row=12, column=3)
		
		self.bouton_start = tk.Button(self, text='▶', bg='lightgreen')
		self.bouton_start.bind('<Button-1>', self.start)
		self.bouton_start.grid(row=11, column=3)
		
		self.bouton_restart = tk.Button(self, text='▶', bg='lightgreen')
		
		#Exit button
		self.exit_bouton = tk.Button(self, text="Quitter", command=self.destroy)
		self.exit_bouton.bind('<Button-1>',self.quitter)
		self.exit_bouton.grid()
	
	def quitter(self, event):
		"""
		Quitter l'application
		"""
		self.destroy()  

	def start(self, event) : 
		"""
		Démarrage de l'enregistrement, création boutons pause et arret
		"""
		self.running = True
		self.server_event.set()
		
		self.bouton_pause = tk.Button(self, text='▌▌', bg='lightyellow')
		self.bouton_pause.bind('<Button-1>', self.pause)
		self.bouton_pause.grid(row=11, column=2)
		
		self.bouton_arret = tk.Button(self, text='◼', bg='red')
		self.bouton_arret.bind( '<Button-1>', self.arret)
		self.bouton_arret.grid(row=11, column=4)
		
		self.bouton_start.destroy()
		self.update_time()

	def update_time(self):
		"""
		Mise à jour du temps
		"""
		if self.running == True :
			self.duree +=1
			minutes = self.duree // 60
			heures = minutes // 60
			secondes = self.duree - minutes * 60 - heures * 3600
			self.chrono.config(text=f'{heures:02}:{minutes:02}:{secondes:02}')
			self.after(1000, self.update_time)

	def pause(self, event) :
		"""
		Pause de l'enregistrement
		"""
		self.running = False
		self.server_event.clear()

		self.bouton_pause.destroy()
		self.bouton_restart = tk.Button(self, text='▶', bg='lightgreen')
		self.bouton_restart.bind('<Button-1>', self.restart)
		self.bouton_restart.grid(row=11, column=2)

	def restart(self, event) :
		"""
		Reprise de l'enregistrement
		"""
		self.running = True
		self.server_event.set()

		self.bouton_restart.destroy()

		self.bouton_pause = tk.Button(self, text='▌▌', bg='lightyellow')
		self.bouton_pause.bind('<Button-1>', self.pause)
		self.bouton_pause.grid(row=11, column=2)
		
		self.update_time()

	def arret(self, event) :
		"""
		Arrêt de l'enregistrement
		"""
		self.running = False
		self.server_event.clear()

		self.duree_memo = self.duree
		self.duree = 0
		self.chrono.config(text='00:00:00')
		self.bouton_arret.destroy()
		self.bouton_restart.destroy()
		self.bouton_pause.destroy()
		self.bouton_start = tk.Button(self, text='▶', bg='lightgreen')
		self.bouton_start.bind('<Button-1>', self.start)
		self.bouton_start.grid(row=11, column=3)
	
		text = cp.comparaison(data_th, mvt_exp) 
		self.resultat = messagebox.showinfo(title='Info', message=text)
		
		self.choix_sauvegarde = messagebox.askquestion(message='Voulez vous sauvegarder votre enregistrement ?', type='yesno')
		
		if self.choix_sauvegarde == 'yes' :
			self.Sauvegarde()
			
			

	def Sauvegarde(self):
		namewin = nameWin(self)
		nom = namewin.nom
		db.add_movement_data(self.user_id, 1, time.strftime('%Y-%m-%d %H:%M:%S'), nom)
		for mesure in mvt_exp:
			db.add_mesure_vect(mesure.idCapteur, mesure.idPaquet, mesure.idDonneeMouvement, mesure.date, mesure.x, mesure.y, mesure.z)
		

	def afficher_historique(self, event):
		"""
		Affichage de l'historique (remplacer la liste )
		"""
		self.frame_pre_enregistrement.grid_forget()
		self.frame_historique.grid(column=0,columnspan= 3,row=2,rowspan = 9,sticky='nesw')

	def afficher_preenregistrement(self, event):
		"""
		Affichage du pré-enregistrement (remplacer la liste )
		"""
		self.frame_historique.grid_forget()
		self.frame_pre_enregistrement.grid(column=0,columnspan= 3,row=2,rowspan = 9,sticky='nesw')
														 
if __name__ == "__main__":
	fen = MainWin()
	fen.mainloop()