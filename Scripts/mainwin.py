'''
Affichage de la Fenêtre Principale
'''
import datetime 
import queue
import tkinter as tk
from tkinter import messagebox
from dataclass import *
from database import db
import perceptron
import comparaison as cp
from server import DataServer
import namewin
from tkinter import font

mvt_exp = MesureVect.from_raw_list([(0,0,1,2,3,1),(1,1,4,5,6,2),(2,2,7,8,9,3)])
data_th = {"aurevoir":MesureVect.from_raw_list([(0,3,10,9,8,1),(0,4,7,6,5,1.5),(0,5,4,3,2,2),(0,6,1,1,1,2.6),(0,7,1,2,3,3)]),
					 "coucou":MesureVect.from_raw_list([(0,13,1,2,3,1),(0,12,4,5,6,1.5),(0,11,7,8,9,2),(0,10,1,1,1,2.6),(0,9,1,2,3,3),(0,8,0,0,0,4)])}

class MainWin(tk.Tk, DataServer):
	def __init__(self, user_id):
		super().__init__()
		DataServer.__init__(self)
		self.user = db.get_user(user_id)


		self.title('G.M.T.')
		# récuperation de la résolution de l'écran
		screen_width = self.winfo_screenwidth()
		screen_height = self.winfo_screenheight() - 100

		self.geometry(f"{screen_width}x{screen_height}")
		self.creer_widgets()

	def creer_widgets(self):
		"""
		Création des widgets
		"""
		# Configuration des colonnes/lignes pour qu'elles se redimensionnent
		for i in range(0,8) :
			self.columnconfigure(i, weight=1)
			self.rowconfigure(i, weight=1)

		#Label tout en haut
		self.title_font = font.Font(family="Bahnschrift SemiBold Condensed", size=16)
		self.label = tk.Label(self, text="ENTRAINEMENT G.M.T", font=self.title_font, fg='#93B2DB')
		self.rowconfigure(0, weight=0)
		self.columnconfigure(0, weight=0)
		self.columnconfigure(1, weight=0)
		self.label.grid(row=0, column=0, columnspan=8)

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

		self.scrollbar.config(command = self.list_historique.yview )

		#Frame pré-enregistrement
		self.frame_pre_enregistrement = tk.Frame(self)

		#Scrollbar a droite de la liste pour le pré-enregistrement
		self.scrollbar_pre_enregistrement = tk.Scrollbar(self.frame_pre_enregistrement)
		self.scrollbar_pre_enregistrement.grid(column=1,row=0, sticky='nesw')


		#Liste pré enregistrement
		self.list_pre_enregistrement = tk.Listbox(self.frame_pre_enregistrement, yscrollcommand=self.scrollbar_pre_enregistrement.set)
		self.list_pre_enregistrement.grid(column=0, row=0, sticky='nesw')
        
		self.data_list_historique = db.list_mouvements_info(self.user.idUtilisateur)
		for i in range(len(self.data_list_historique)):
			self.list_historique.insert(tk.END, str(i+1) + ' - ' + str(self.data_list_historique[i].dateCreation) ) 

		self.data_list_pre_enregistrement = db.list_mouvements_info(1) #id 1 pour les pre-enregistrement
		for i in range(len(self.data_list_pre_enregistrement)):
			self.list_pre_enregistrement.insert(tk.END, str(i+1) + ' - ' + str(self.data_list_pre_enregistrement[i].name) )

		self.scrollbar_pre_enregistrement.config(command = self.list_pre_enregistrement.yview )

		#Afficher la frame pré-enregistrement
		self.frame_pre_enregistrement.grid(column=0, columnspan= 2, row=1, rowspan = 9, ipadx=10,  sticky='nesw')
		self.frame_pre_enregistrement.columnconfigure(0, weight = 1)
		self.frame_pre_enregistrement.rowconfigure(0, weight=1)

		#police d'écriture
		self.font = font.Font(family="Bahnschrift SemiLight SemiCondensed", size=8)

		#Bouton pré-enregistrement
		self.button_preenregistrement = tk.Button(self, text="Enregistrement", font=self.font, padx= 10, fg='#353535', bg='#ECFCCA')
		self.button_preenregistrement.bind('<Button-1>', self.afficher_preenregistrement)
		self.button_preenregistrement.grid(column=0, row=0, sticky='nesw')
        
        #Bouton historique
		self.button_historique = tk.Button(self, text="Historique", font=self.font, padx= 20, fg='#353535', bg='#FCEECA')
		self.button_historique.bind('<Button-1>', self.afficher_historique)
		self.button_historique.grid(column=1, row=0, sticky="nesw")
		
		#cadre visualisation
		self.canevas = tk.Canvas(self, background='lightblue')
		self.canevas.grid(column=2,columnspan=6,row=1,rowspan= 10, sticky='nesw')
        
        #ajustement de la taille relative
		#self.canevas.columnconfigure(1, weight=2)
		#self.frame_pre_enregistrement.columnconfigure(1, weight=1)
		
		#gestion enregistrement
		self.start_time = 0
		self.running = False
		self.chrono = tk.Label(text='00:00:00', fg='#444445')
		self.chrono.grid(row=13, column=0, columnspan=8)

		self.label_enregistrement = tk.Label(text="Commencer l'enregistrement", fg='#444445')
		self.label_enregistrement.grid(row=12, column=0, columnspan=8)
		self.precision_var = tk.StringVar()
		self.label_pourcentage = tk.Label(textvariable=self.precision_var, fg='#444445')
		self.label_pourcentage.grid(row=12, column=5)
        
        #image bouton start
		self.img_start = tk.PhotoImage(file='Scripts/images/start.png')
		self.img_pause = tk.PhotoImage(file='Scripts/images/pause.png')
		self.img_stop = tk.PhotoImage(file='Scripts/images/stop.png')
		
		self.bouton_start = tk.Button(self, image=self.img_start)
		self.bouton_start.bind('<Button-1>', self.start)
		self.bouton_start.grid(row=11, column=0, columnspan=8)
		
		self.bouton_restart = tk.Button(self, image=self.img_start)
		
		#Exit button
		self.exit_bouton = tk.Button(self, text="Quitter", command=self.destroy, fg='#444445', bg='#FFE8DF')
		self.exit_bouton.bind('<Button-1>',self.quitter)
		self.exit_bouton.grid(row=14, column=0, columnspan=8)
	
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
		now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		idMvt = db.add_movement_data(self.user.idUtilisateur, 1, now, None)
		self.server_event.idMvt = idMvt
		self.server_event.set()

		#self.get_current_comp()

		while True: # Clear the queue
			try:
				self.dataQueue.get_nowait()
			except queue.Empty:
				break

		self.bouton_pause = tk.Button(self, image=self.img_pause)
		self.bouton_pause.bind('<Button-1>', self.pause)
		self.bouton_pause.grid(row=11, column=3)
		
		self.bouton_arret = tk.Button(self, image=self.img_stop)
		self.bouton_arret.bind( '<Button-1>', self.arret)
		self.bouton_arret.grid(row=11, column=5)
		
		self.bouton_start.destroy()
		self.start_time = datetime.datetime.now()
		self.update_time()

	def update_time(self):
		"""
		Mise à jour du temps
		"""
		if self.running == True :
			d = datetime.datetime.now() - self.start_time
			txt = (datetime.datetime.fromtimestamp(d.total_seconds()) - datetime.timedelta(hours=1)).strftime('%H:%M:%S')
			self.chrono.config(text=txt)
			self.after(1000, self.update_time)

	def pause(self, event) :
		"""
		Pause de l'enregistrement
		"""
		self.running = False
		self.server_event.clear()

		self.bouton_pause.destroy()
		self.bouton_restart = tk.Button(self, image=self.img_start)
		self.bouton_restart.bind('<Button-1>', self.restart)
		self.bouton_restart.grid(row=11, column=3)

	def restart(self, event) :
		"""
		Reprise de l'enregistrement
		"""
		self.running = True
		self.server_event.set()

		self.bouton_restart.destroy()

		self.bouton_pause = tk.Button(self, image=self.img_pause)
		self.bouton_pause.bind('<Button-1>', self.pause)
		self.bouton_pause.grid(row=11, column=3)
		
		self.update_time()

	def arret(self, event) :
		"""
		Arrêt de l'enregistrement
		"""
		self.running = False
		self.server_event.clear()

		self.duree_memo = int((datetime.datetime.now() - self.start_time).total_seconds())
		self.chrono.config(text='00:00:00')
		self.bouton_arret.destroy()
		self.bouton_restart.destroy()
		self.bouton_pause.destroy()
		self.bouton_start = tk.Button(self, image=self.img_start)
		self.bouton_start.bind('<Button-1>', self.start)
		self.bouton_start.grid(row=11, column=0, columnspan=8)

		#self.compare_message()

		self.sauvegarde()		

		

	def sauvegarde(self):
		"""
		Mise dans l'historique ou dans l'enregistrement
		"""

		if not bool(self.user.eleve):
			self.choix_sauvegarde = messagebox.askquestion(message='Voulez-vous sauvegarder votre enregistrement ?', type='yesno')
			if self.choix_sauvegarde == messagebox.YES:
				self.sauvegarde_enregistrement()
				histo = False
			else:
				histo = True
		else:
			histo = True
		
		if histo:
			historique = db.list_mouvements_info(self.user.idUtilisateur)  #Moyen opti :/
			self.list_historique.insert(tk.END, str(len(historique)) + ' - ' + str(historique[-1].dateCreation) ) 


	def compare_message(self) :
		'''
		Affiche l'analyse comparative à partir de la base de donnée
		'''
		mvt_exp = db.get_mesure_vect(self.server_event.idMvt)
		mvt_the = {}
		for li in db.list_mouvements_info(1) :
			id = li.idMvt
			name = li.name
			mvt_the[name] = db.get_mesure_vect(id) 
		text = cp.comparaison_total('a',mvt_the, mvt_exp) # à adapter avec l'apprentissage 
		self.resultat = messagebox.showinfo(title='Info', message=text)


	def afficher_historique(self, event):
		"""
		Affichage de l'historique (remplacer la liste )
		"""
		self.frame_pre_enregistrement.grid_forget()
		self.frame_historique.grid(column=0,columnspan= 2,row=1,rowspan = 9,sticky='nesw')

	def afficher_preenregistrement(self, event):
		"""
		Affichage du pré-enregistrement (remplacer la liste )
		"""
		self.frame_historique.grid_forget()
		self.frame_pre_enregistrement.grid(column=0,columnspan= 2,row=1,rowspan = 9,sticky='nesw')		

	def sauvegarde_enregistrement(self):

		def callback(nom):
			if nom:
				idmvt = self.server_event.idMvt 
				db.rename_donnees(idmvt,nom)
				enregistrement = db.list_mouvements_info(1) #id 1 pour les pre-enregistrement
				self.list_pre_enregistrement.insert(tk.END, str(len(enregistrement)) + ' - ' + str(enregistrement[-1].name) )

		namewin.NameWin(callback)


		

	def get_current_comp(self):
		if not self.running:
			return
		data = []
		
		while True: # Get all data from queue
			try:
				data.append(self.dataQueue.get_nowait())
			except queue.Empty:
				break

		data_th = perceptron.predict(data)

		value = cp.comparaison(data_th, data)

		print(f'{value=}')
		self.precision_var.set(f'{value=}%')
		# TODO - Update StringVar
  
		self.after(1000, self.get_current_comp)

if __name__ == "__main__":
	fen = MainWin(10) #1 admin, #10 test #19 test_teacher #20 test_eleve
	fen.mainloop()	