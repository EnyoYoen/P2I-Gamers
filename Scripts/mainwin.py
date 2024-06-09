'''
Affichage de la Fenêtre Principale
'''
import datetime 
import json
import math
import multiprocessing
import os
import queue
import threading
import time
import tkinter as tk
import itertools
from PIL import Image, ImageTk
import ctypes

from secret import CALIBRATION_FILE

from graphs import *
from dataclass import *
from database import Database
import perceptron
import comparaison as cp
from server import DataServer
import namewin
import calibration_popup

import pandas as pd

# from tkinter import font
# from tkinter import messagebox
# import matplotlib
# matplotlib.use("TkAgg")
# from matplotlib import style
# style.use('ggplot')

mvt_exp = MesureVect.from_raw_list([(0,0,1,2,3,1),(1,1,4,5,6,2),(2,2,7,8,9,3)])
data_th = {"aurevoir":MesureVect.from_raw_list([(0,3,10,9,8,1),(0,4,7,6,5,1.5),(0,5,4,3,2,2),(0,6,1,1,1,2.6),(0,7,1,2,3,3)]),
					 "coucou":MesureVect.from_raw_list([(0,13,1,2,3,1),(0,12,4,5,6,1.5),(0,11,7,8,9,2),(0,10,1,1,1,2.6),(0,9,1,2,3,3),(0,8,0,0,0,4)])}

class MainWin():
	def __init__(self, user_id):
		super().__init__()
		self.db = Database()
		self.user = self.db.get_user(user_id)
		self.root = tk.Tk()
		
		self.mlp, self.factor_to_label = perceptron.load_MLP()
		self.typesCapteurs = {}

		for type in self.db.list_type_capteurs():
			self.typesCapteurs[type.idPlacement] = type
		self.capteurs = {}
		for capteur in self.db.list_capteurs():
			self.capteurs[capteur.idCapteur] = capteur
   
		self.root.title('G.M.T.')
		# récuperation de la résolution de l'écran
		screen_width = self.root.winfo_screenwidth()
		screen_height = self.root.winfo_screenheight() - 100

		self.root.geometry(f"{screen_width}x{screen_height}")

		manager = multiprocessing.Manager()
		self.is_calibrating = manager.Value('b', False)
		self.is_comparaison = manager.Value('b', True)
		self.running = manager.Value('b', False)

		# self.f = Figure(figsize=(2,2), dpi=100)
		# self.a = self.f.add_subplot(111)

		self.creer_widgets()


		self.data_server = DataServer()
		for k in ('server_event', 'dataQueue', 'gui_data_queue', 'idMvt', 'calibration_data'):
			setattr(self, k, getattr(self.data_server, k))

		self.graph_queue, self.precision_var_proxy = get_current_comp(self)
		self.update_plots()

		self.root.mainloop()

	def creer_widgets(self):
		"""
		Création des widgets
		"""
		# Configuration des colonnes/lignes pour qu'elles se redimensionnent
		for i in range(0,8) :
			self.root.columnconfigure(i, weight=1)
			self.root.rowconfigure(i, weight=1)

		#image du logo
		self.img_logo_pil = Image.open('Scripts/images/logo.png')
		self.img_logo_resize = self.img_logo_pil.resize((50, 30), Image.LANCZOS)
		self.img_logo = ImageTk.PhotoImage(self.img_logo_resize)
		self.label_logo = tk.Label(self.root, image=self.img_logo)
		self.label_logo.grid(row=0, column=4)

		#icone de la fenetre
		self.img_logo_resize = self.img_logo_pil.resize((100, 85), Image.LANCZOS)
		self.icon_image = ImageTk.PhotoImage(self.img_logo_resize)
		self.root.iconphoto(True, self.icon_image)
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'id')

		#Label tout en haut
		self.title_font = tk.font.Font(family="Bahnschrift SemiBold Condensed", size=16)
		self.label = tk.Label(self.root, text="ENTRAINEMENT G.M.T", font=self.title_font, fg='#93B2DB')

		self.root.rowconfigure(0, weight=0) # ???
		self.root.columnconfigure(0, weight=0)
		self.root.columnconfigure(1, weight=0)

		self.label.grid(row=0, column=4, columnspan=2)

		#Frame historique
		self.frame_historique = tk.Frame(self.root)
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
		self.frame_pre_enregistrement = tk.Frame(self.root)

		#Scrollbar a droite de la liste pour le pré-enregistrement
		self.scrollbar_pre_enregistrement = tk.Scrollbar(self.frame_pre_enregistrement)
		self.scrollbar_pre_enregistrement.grid(column=1,row=0, sticky='nesw')


		#Liste pré enregistrement
		self.list_pre_enregistrement = tk.Listbox(self.frame_pre_enregistrement, yscrollcommand=self.scrollbar_pre_enregistrement.set)
		self.list_pre_enregistrement.grid(column=0, row=0, sticky='nesw')
		
		# TODO - C'est pas bien ca
		self.data_list_historique = self.db.list_mouvements_info(1)
		# self.data_list_historique = self.db.list_mouvements_info(self.user.idUtilisateur)
		for i in range(len(self.data_list_historique)):
			self.list_historique.insert(tk.END, str(i+1) + ' - ' + str(self.data_list_historique[i].dateCreation) ) 

		self.data_list_pre_enregistrement = self.db.list_mouvements_info(1) #id 1 pour les pre-enregistrement
		for i in range(len(self.data_list_pre_enregistrement)):
			self.list_pre_enregistrement.insert(tk.END, str(i+1) + ' - ' + str(self.data_list_pre_enregistrement[i].name) )

		self.scrollbar_pre_enregistrement.config(command = self.list_pre_enregistrement.yview )

		#Afficher la frame pré-enregistrement
		self.frame_pre_enregistrement.grid(column=0, columnspan= 2, row=1, rowspan = 9, ipadx=10,  sticky='nesw')
		self.frame_pre_enregistrement.columnconfigure(0, weight = 1)
		self.frame_pre_enregistrement.rowconfigure(0, weight=1)

		#police d'écriture
		self.font = tk.font.Font(family="Bahnschrift SemiLight SemiCondensed", size=8)

		#Bouton pré-enregistrement
		self.button_preenregistrement = tk.Button(self.root, text="Enregistrement", font=self.font, padx= 10, fg='#353535', bg='#ECFCCA')
		self.button_preenregistrement.bind('<Button-1>', self.afficher_preenregistrement)
		self.button_preenregistrement.grid(column=0, row=0, sticky='nesw')
		
		#Bouton historique
		self.button_historique = tk.Button(self.root, text="Historique", font=self.font, padx= 20, fg='#353535', bg='#FCEECA')
		self.button_historique.bind('<Button-1>', self.afficher_historique)
		self.button_historique.grid(column=1, row=0, sticky="nesw")
		
		#cadre visualisation
		self.canevas = tk.Canvas(self.root, background='lightblue')
		self.canevas.grid(column=2,columnspan=5,row=1,rowspan= 10, sticky='nesw')
		
		#ajustement de la taille relative
		#self.canevas.columnconfigure(1, weight=2)
		#self.frame_pre_enregistrement.columnconfigure(1, weight=1)
		
		#gestion enregistrement
		self.start_time = 0
		self.chrono = tk.Label(self.root, text='00:00:00', fg='#444445')
		self.chrono.grid(row=13, column=4)

		self.label_enregistrement = tk.Label(self.root, text="Commencer l'enregistrement", fg='#444445')
		self.label_enregistrement.grid(row=12, column=4)


		self.precision_var = tk.StringVar()
		self.label_pourcentage = tk.Label(self.root, textvariable=self.precision_var, fg='#444445')
		self.label_pourcentage.grid(row=12, column=5)
		
		#image bouton start
		self.img_start = tk.PhotoImage(file='Scripts/images/start.png')
		self.img_pause = tk.PhotoImage(file='Scripts/images/pause.png')
		self.img_stop = tk.PhotoImage(file='Scripts/images/stop.png')
		
		self.bouton_start = tk.Button(self.root, image=self.img_start)
		self.bouton_start.bind('<Button-1>', self.start)
		self.root.bind('<space>', self.start)
		self.bouton_start.grid(row=11, column=4)
		
		self.bouton_restart = tk.Button(self.root, image=self.img_start)

		#Button 
		self.bouton_desac_compa = tk.Button(self.root, text='Désactiver comparaison')
		self.bouton_desac_compa.bind('<Button-1>', self.off_compa)
		self.bouton_desac_compa.grid(row=11, column=7)

		self.bouton_act_compa = tk.Button(self.root, text='Activer comparaison')
		self.bouton_act_compa.bind('<Button-1>', self.on_compa)

		#Button 
		self.bouton_calibration = tk.Button(self.root, text='Calibrage')
		self.bouton_calibration.bind('<Button-1>', self.start_calibration)
		self.bouton_calibration.grid(row=12, column=7)

		# #Exit button
		# self.exit_bouton = tk.Button(self.root, text="Quitter", command=self.root.destroy, fg='#444445', bg='#FFE8DF')
		# self.exit_bouton.bind('<Button-1>',self.quitter)
		# self.exit_bouton.grid(row=14, column=5)

		# Graphs
		
		graphs_class = {
			'line': LineGraph,
			'3D': Graph3D,
			'boxplot': BoxPlot,
			'line2': LineGraph,
		}
		kwargs = {
			'3D': {'xlim': (-1, 1), 'ylim': (-1, 1), 'zlim': (-1, 1)}
		}
		self.graph_frame = Frame(self.root, bg='red')
		self.graphs = Graphs(self.graph_frame, graphs_class, kwargs)
		self.graph_frame.grid(row=1, column=7, rowspan=10, columnspan=1, sticky='nesw')

	def off_compa(self, event):
		self.is_comparaison.set(False)
		self.bouton_desac_compa.grid_forget()
		self.bouton_act_compa.grid(row=11, column=7)

	def on_compa(self, event):
		self.is_comparaison.set(True)
		self.bouton_act_compa.grid_forget()
		self.bouton_desac_compa.grid(row=11, column=7)

	def quitter(self, event):
		"""
		Quitter l'application
		"""
		self.destroy()  

	def start(self, event) : 
		"""
		Démarrage de l'enregistrement, création boutons pause et arret
		"""
		self.running.set(True)

		self.bouton_pause = tk.Button(self.root, image=self.img_pause)
		self.bouton_pause.bind('<Button-1>', self.pause)
		self.bouton_pause.grid(row=11, column=3)
		
		self.bouton_arret = tk.Button(self.root, image=self.img_stop)
		self.bouton_arret.bind( '<Button-1>', self.arret)
		self.root.bind('<space>', self.arret)
		self.bouton_arret.grid(row=11, column=5)
		
		self.bouton_start.destroy()
		self.start_time = datetime.datetime.now()
		self.update_time()

		self.idMvt.set(self.db.add_movement_data(self.user.idUtilisateur, 1, self.start_time.strftime('%Y-%m-%d %H:%M:%S.%f'), None))

		while True: # Clear the queue
			try:
				self.dataQueue.get_nowait()
			except queue.Empty:
				break
		self.server_event.set()

	def update_time(self):
		"""
		Mise à jour du temps
		"""
		if self.running.value == True :
			d = datetime.datetime.now() - self.start_time
			txt = (datetime.datetime.fromtimestamp(d.total_seconds()) - datetime.timedelta(hours=1)).strftime('%H:%M:%S')
			self.chrono.config(text=txt)
			self.root.after(1000, self.update_time)

	def pause(self, event) :
		"""
		Pause de l'enregistrement
		"""
		self.running.set(False)
		self.server_event.clear()

		self.bouton_pause.destroy()
		self.bouton_restart = tk.Button(self.root, image=self.img_start)
		self.bouton_restart.bind('<Button-1>', self.restart)
		self.bouton_restart.grid(row=11, column=3)

	def restart(self, event) :
		"""
		Reprise de l'enregistrement
		"""
		self.running.set(True)
		self.server_event.set()

		self.bouton_restart.destroy()

		self.bouton_pause = tk.Button(self.root, image=self.img_pause)
		self.bouton_pause.bind('<Button-1>', self.pause)
		self.bouton_pause.grid(row=11, column=3)

		self.update_time()

	def arret(self, event) :
		"""
		Arrêt de l'enregistrement
		"""
		self.running.set(False)
		self.server_event.clear()

		self.duree_memo = int((datetime.datetime.now() - self.start_time).total_seconds())
		self.chrono.config(text='00:00:00')
		self.bouton_arret.destroy()
		self.bouton_restart.destroy()
		self.bouton_pause.destroy()
		self.bouton_start = tk.Button(self.root, image=self.img_start)
		self.bouton_start.bind('<Button-1>', self.start)
		self.root.bind('<space>', self.start)
		self.bouton_start.grid(row=11, column=4)
		

		#self.compare_message()

		self.sauvegarde()

	def sauvegarde(self):
		"""
		Mise dans l'historique ou dans l'enregistrement
		"""

		if not bool(self.user.eleve):
			self.choix_sauvegarde = tk.messagebox.askquestion(message='Voulez-vous sauvegarder votre enregistrement ?', type='yesno')
			if self.choix_sauvegarde == tk.messagebox.YES:
				self.sauvegarde_enregistrement()
				histo = False
			else:
				histo = True
		else:
			histo = True
		
		if histo:
			historique = self.db.list_mouvements_info(self.user.idUtilisateur)  #Moyen opti :/
			self.list_historique.insert(tk.END, str(len(historique)) + ' - ' + str(historique[-1].dateCreation) ) 

	def compare_message(self) :
		'''
		Affiche l'analyse comparative à partir de la base de donnée
		'''
		mvt_the = {}
		name_predict = self.factor_to_label[perceptron.predict(self.mlp, perceptron.convert_to_sequence(perceptron.get_mesure_list(self.idMvt.value, self.db)))]
		for li in self.db.list_mouvements_info(1) :
			id = li.idMvt
			name = li.name
			mvt_the[name] = self.db.get_mesure_vect(id) 
		text = cp.comparaison_total(name_predict, mvt_the, mvt_exp) 
		self.resultat = tk.messagebox.showinfo(title='Info', message=text)

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
				idmvt = self.idMvt.value
				self.db.rename_donnees(idmvt,nom)
				enregistrement = self.db.list_mouvements_info(1) #id 1 pour les pre-enregistrement
				self.list_pre_enregistrement.insert(tk.END, str(len(enregistrement)) + ' - ' + str(enregistrement[-1].name) )

		namewin.NameWin(callback)

	def update_plots(self):
		self.root.after(100, self.update_plots)

		self.precision_var.set(f'{self.precision_var_proxy.value} %')

		while not self.graph_queue.empty():
			packet = self.graph_queue.get()
			for data in packet:
				if data[0] is None and data[1] == 'UPDATE':
					self.graphs.update(data[2])
				else:
					self.graphs.add_data(*data)

		self.graphs.plot()

	def start_calibration(self, *args):
		if os.path.exists(CALIBRATION_FILE):
			os.remove(CALIBRATION_FILE)

		self.is_calibrating.set(True)
		self.calibration_data = None

		# Empty data queue
		while True:
			try:
				self.dataQueue.get_nowait()
			except queue.Empty:
				break

		calibration_popup.calibration_popup()

		self.root.after(5000, self.finish_calibration)

	def finish_calibration(self):
		def iterator():
			while True: # Get all data from queue
				try:
					yield self.dataQueue.get_nowait()
				except queue.Empty:
					break

		calibration_data = {}

		for mesure in iterator():
			if isinstance(mesure, MesureSimple):
				if mesure.idCapteur < 5:
					continue

				ind = mesure.idCapteur
				val = mesure.valeur

				if ind not in calibration_data:
					calibration_data[ind] = [-math.inf, math.inf]

				if val > calibration_data[ind][0]:
					calibration_data[ind][0] = val
				if val < calibration_data[ind][1]:
					calibration_data[ind][1] = val

			elif isinstance(mesure, MesureVect):
				ind = mesure.idCapteur
				vec = mesure.X, mesure.Y, mesure.Z

				if ind not in calibration_data:
					calibration_data[ind] = [[mesure.X], [mesure.Y], [mesure.Z]]
				else:
					for i, v in enumerate(vec):
						calibration_data[ind][i].append(v)

		for ind, data in calibration_data.items():
			if 11 <= ind:
				vec = [sum(calibration_data[ind][i]) / len(calibration_data[ind][i]) for i in range(3)]
				teta = math.atan(vec[1] / vec[0])
				phi = math.acos(vec[2] / (vec[0]**2 + vec[1]**2 + vec[2]**2)**0.5) 

				calibration_data[ind] = [teta, phi]

		with open(CALIBRATION_FILE, 'w') as f:
			json.dump(calibration_data, f)
		
		self.calibration_data = calibration_data
		self.is_calibrating.set(False)

		print('Calibration complete')


# Multiprocessing functions
def get_current_comp(self, thread=False): # TODO - Put this in a different process
	# /!\ Ici, self est juste la reference a l'objet, ce n'est pas une methode!
	if not thread:
		# self.update_plots()
		# threading.Thread(target=self.get_current_comp, args=(True,), daemon=True).start()

		manager = multiprocessing.Manager()
		self.comp_ns = manager.Namespace()
		self.comp_ns.precision_var = manager.Value('d', 0.0)
		self.comp_ns.graph_queue = manager.Queue()
		self.comp_ns.dataQueue = self.dataQueue

		for k in ('running', 'is_comparaison', 'is_calibrating', 'idMvt'):
			setattr(self.comp_ns, k, getattr(self, k)) # TODO - Graphs proxy

		multiprocessing.Process(target=get_current_comp, args=(self.comp_ns, True,), daemon=True).start()
		return self.comp_ns.graph_queue, self.comp_ns.precision_var

	db = Database()
	
	self.mlp, self.factor_to_label = perceptron.load_MLP()

	# while True: # Clear all data from queue -> because otherwise we jsut spend way too long processing old data
	# 	try:
	# 		self.dataQueue.get_nowait()
	# 	except queue.Empty:
	# 		break

	convert_date = lambda i: datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f').timestamp()

	while True:

		try:
			if self.is_calibrating.value:
				# Don't take data during calibration
				time.sleep(0.5)
				continue

			data = [self.dataQueue.get()]

			counter = 0
			while True: # Get all data from queue
				try:
					mesure = self.dataQueue.get_nowait()
					counter += 1
					if time.time() - convert_date(mesure.dateCreation) > 10: # Don't save old data
						continue
					data.append(mesure)
				except queue.Empty:
					break
				# if len(data) >= 100:
				# 	break

			if not data:
				continue

			if len(data) > 100:
				print('TOO MUCH DATA, dropping everything', len(data), flush=True)
			else:
				add_data_sensors(self, data)

			if self.running.value and self.is_comparaison.value:
				try:
					USE_PERCEPTRON = True
					if USE_PERCEPTRON:
						try:
							label = self.factor_to_label[perceptron.predict(
								self.mlp, 
								pd.DataFrame(np.array([perceptron.convert_to_sequence(
									perceptron.get_mesure_list(
										326, 
										db
							)).flatten()])))[0]]
						except Exception as e:
							print(f'Erreur du perceptron: {e}')
							pass
							label = None

						print(f'{label=}')
						if label is not None:
							mouvements = db.list_mouvements_info(1)

							for mouvement in mouvements:
								if mouvement.name == label:
									idMvtTh = mouvement.idMvt
									break
							else:
								idMvtTh = None
						else:
							idMvtTh = None
					else:
						idMvtTh = 329

					if idMvtTh is not None:
						mvmt_info_exp, mesures_simple_exp, mesures_vect_exp = db.get_mouvement(self.idMvt.value)

						if len(mesures_simple_exp) != 0 and len(mesures_vect_exp) != 0:

							try:
								# value = cp.comparaison_direct(data_th, data_exp)
								value = cp.comparaison_direct2(mesures_simple_exp, mesures_vect_exp, idMvtTh)

								print(f'{value=}')
								self.precision_var.set(value)
							except Exception as e:
								print(f'Erreur pendant la comparaison: {e}')
								pass

							packet = []
							packet.append(('line2', 1, ([datetime.datetime.now().timestamp()], [value]), None, 20))
							packet.append(('line2', 2, ([datetime.datetime.now().timestamp()], [100]), 1))
							packet.append(('line2', 3, ([datetime.datetime.now().timestamp()], [0]), 1))
							packet.append(('boxplot', 1, ([datetime.datetime.now().timestamp()], [value]), None, 20))

							self.graph_queue.put(packet)
	
					# self.graphs.add_data('line2', 1, [datetime.datetime.now().timestamp()], [value], value_limit=20)
					# self.graphs.add_data('line2', 2, [datetime.datetime.now().timestamp()], [100], limit=1) # Prevent resize
					# self.graphs.add_data('line2', 3, [datetime.datetime.now().timestamp()], [0], limit=1)

					# self.graphs.add_data('boxplot', 1, [datetime.datetime.now().timestamp()], [value], value_limit=20)

				except Exception as e:
					print(f'Erreur apres la comparaison: {e}')
					pass

		except EOFError:
			break # Program is shutting down
		except BrokenPipeError:
			break # Same
		except multiprocessing.managers.RemoteError:
			break # Same
	print('Stopped comparing')

def add_data_sensors(self, liste:list):
	convert_date = lambda i: datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f').timestamp()

	packet = []

	for obj in liste:
		try:
			if isinstance(obj, MesureSimple):
				# if obj.idCapteur < 6: continue
				now = convert_date(obj.dateCreation)
				# self.graphs.add_data('line', obj.idCapteur, [now], [obj.valeur], value_limit=now-20) # last 20 sec
				off = 1

				packet.append(('line', obj.idCapteur, ([now], [obj.valeur]), None, now-20))

				packet.append(('line', 11, ([now], [0]), 1)) # prevent auto-resize
				packet.append(('line', 12, ([now], [off]), 1))

				# self.graphs.add_data('line', 11, [now], [0], limit=1) # prevent auto-resize
				# self.graphs.add_data('line', 12, [now], [off], limit=1)

			if isinstance(obj, MesureVect):
				if obj.idCapteur >= 17 and obj.idCapteur%3==2:
					# self.graphs.add_data('3D', obj.idCapteur, [obj.X, 0], [obj.Y, 0], [obj.Z, 0], limit=2)
					off = 1

					packet.append(('3D', obj.idCapteur, ([obj.X, 0], [obj.Y, 0], [obj.Z, 0]), 2))

					# self.graphs.add_data('3D', 1, *[[-off]]*3, limit=1) # prevent auto-resize
					# self.graphs.add_data('3D', 2, *[[off]]*3, limit=1)
					packet.append(('3D', 1, [[-off]]*3, 1)) # prevent auto-resize
					packet.append(('3D', 2, [[off]]*3, 1))
		except multiprocessing.managers.RemoteError:
			# Program has ended
			return

	packet.append((None, 'UPDATE', 'line'))
	packet.append((None, 'UPDATE', '3D'))
 
	self.graph_queue.put(packet)

	# self.graphs.update('line')
	# self.graphs.update('3D')
	# self.graphs.plot()

if __name__ == "__main__":
		fen = MainWin(19) #1 admin, #10 test #19 test_teacher #20 test_eleve