from datetime import datetime
import time
from dataclass import *
import secret
import mysql.connector as mysql


class Database:
	"""Gestion de la base de donnée"""
	def __init__(self):
		self.connexion_bd = None
		self.connexion()
		
	def connexion(self):
		try:
			self.connexion_bd = mysql.connect(**secret.DATABASE_LOGIN)
			print(f"=> Connexion à {secret.DATABASE_LOGIN['database']} établie...")
		except Exception as e:
			print('MySQL [CONNEXION ERROR]')
			print(e)
		return self.connexion_bd

	def sql(self, sql, params=None):
		try:
			cursor = self.connexion_bd.cursor()
			cursor.execute(sql, params or [])
		except Exception as e:
			print('MySQL [SQL ERROR]')
			print(e)
			raise
		out = cursor.fetchall()
		return out

	def save(self):
		self.connexion_bd.commit()

	@MouvementInfo.cast
	def list_mouvements_info(self, id_user: int) -> list:
		"""Renvoie la liste de tous les mouvements de l'user mis en paramètre"""
		sql = "SELECT * FROM DonneesMouvements" # TODO !!
		print( self.sql(sql))
		return self.sql(sql)

	@MouvementInfo.cast_single
	def get_mouvements_info(self, idMouvement):
		"""Renvoie les infos associees a un mouvement idMouvement"""
		sql = "SELECT * FROM DonneesMouvements WHERE idMouvement=%s"
		return self.sql(sql, [idMouvement])[0]

	@MesureSimple.cast
	def get_mesure_simple(self, idMouvement):
		"""Renvoie la liste de mesures simples correspondant au mouvement idMouvement"""
		sql = "SELECT * FROM MesuresSimples WHERE idMouvement = %s"
		return self.sql(sql, [idMouvement])

	@MesureVect.cast
	def get_mesure_vect(self, idMouvement):
		"""Renvoie la liste de mesures vectorielles correspondant au mouvement idMouvement"""
		sql = "SELECT * FROM MesuresVect WHERE idMouvement = %s"
		return self.sql(sql, [idMouvement])

	def get_mouvement(self, idMouvement):
		"""Renvoie toutes les données associées à idMouvement"""
		return self.get_mouvements_info(idMouvement), self.get_mesure_simple(idMouvement), self.get_mesure_vect(idMouvement)

	@Paquet.cast
	def list_packets(self, idMouvement=None):
		"""Renvoie la liste des paquets
		Filtre optionnel sur un mouvement idMouvement
		"""
		sql = "SELECT * FROM Paquets"
		params = []
		if idMouvement is not None:
			sql += " WHERE idPaquet IN (SELECT idPaquet FROM MesuresSimples WHERE idMouvement = %s) OR idPaquet IN (SELECT idPaquet FROM MesuresVect WHERE idMouvement = %s)"
			params = [idMouvement, idMouvement]

		return self.sql(sql, params)

	@Capteur.cast
	def list_capteurs(self):
		"""Renvoie la liste des capteurs"""
		sql = "SELECT * FROM Capteurs"
		return self.sql(sql)

	@Capteur.cast_single
	def get_capteur(self, idCapteur):
		"""Renvoie le capteur correspondant à idCapteur"""
		sql = "SELECT * FROM Capteurs WHERE idCapteur=%s"
		return self.sql(sql, [idCapteur])[0]

	@Utilisateur.cast
	def list_users(self):
		"""Renvoie la liste des utilisateurs"""
		sql = "SELECT * FROM Utilisateurs"
		return self.sql(sql)

	@Utilisateur.cast_single
	def get_user(self, idUser):
		"""Renvoie l'utilisateur correspondant à idUser"""
		sql = "SELECT * FROM Utilisateurs WHERE idUtilisateur=%s"
		return self.sql(sql, [idUser])[0]

	@Utilisateur.cast_single
	def get_user_by_name(self, username):
		"""Renvoie l'utilisateur correspondant à idUser"""
		sql = "SELECT * FROM Utilisateurs WHERE nomUtilisateur=%s"
		return self.sql(sql, [username])[0]


	def add_paquet(self, size):
		"""Ajoute un paquet de taille size"""
		sql = "INSERT INTO Paquets (taille) VALUES (%s);"
		self.sql(sql, [size])
		self.save()

	def add_sensor_type(self, type, manufacturer, name):
		"""Ajoute un type de capteur"""
		sql = "INSERT INTO TypeCapteurs (type, fabricant, nomCapteur) VALUES (%s, %s, %s);"
		self.sql(sql, [type, manufacturer, name])
		self.save()

	def add_sensor(self, idPlacement, idDispositif, installDate, uninstallDate = None):
		"""Ajoute un capteur"""
		if uninstallDate is None:
			sql = "INSERT INTO Capteurs (idPlacement, idDispositif, dateInsta) VALUES (%s, %s);"
			self.sql(sql, [idPlacement, idDispositif, installDate])
		else:	
			sql = "INSERT INTO Capteurs (idPlacement, idDispositif, dateInsta, dateDesinsta) VALUES (%s, %s, %s);"
			self.sql(sql, [idPlacement, idDispositif, installDate, uninstallDate])
		self.save()

	def add_contraption(self, name):
		"""Ajoute un dispositif"""
		sql = "INSERT INTO Dispositifs (nom) VALUES (%s)"
		self.sql(sql, [name])
		self.save()

	def add_mesure_simple(self, idCapteur, idPaquet, idDonneeMouvement, date, value, save=True):
		"""Ajoute une mesure simple"""
		sql = "INSERT INTO MesuresSimples (idCapteur, idPaquet, idDonneeMouvement, date, valeur) VALUES (%s, %s, %s, %s, %s);"
		self.sql(sql, [idCapteur, idPaquet, idDonneeMouvement, date, value])
		if save:
			self.save()

	def add_mesure_vect(self, idCapteur, idPaquet, idDonneeMouvement, date, x, y, z, save=True):
		"""Ajoute une mesure vectorielle"""
		sql = "INSERT INTO MesuresVect (idCapteur, idPaquet, idDonneeMouvement, date, x, y, z) VALUES (%s, %s, %s, %s, %s, %s, %s);"
		self.sql(sql, [idCapteur, idPaquet, idDonneeMouvement, date, x, y, z])
		if save:
			self.save()

	def add_mesures_multiples(self, simples, vects, save=True):
		"""Ajoute un ensemble de mesures simples et vectorielles"""
		v = ", ".join(["(%s, %s, %s, %s, %s, %s, %s)"] * len(vects))
		sql = "INSERT INTO MesuresVect (idCapteur, idPaquet, idDonneeMouvement, date, x, y, z) VALUES " + v
		data = []
		for vect in vects:
			data.extend(vect)
		self.sql(sql, data)

		v = ", ".join(["(%s, %s, %s, %s, %s)"] * len(simples))
		sql = "INSERT INTO MesuresSimples (idCapteur, idPaquet, idDonneeMouvement, date, valeur) VALUES " + v
		data = []
		for simple in simples:
			data.extend(simple)
		self.sql(sql, data)

		if save:
			self.save()


	def add_user(self, name, password, height, is_student):
		"""Ajoute un utilisateur"""
		sql = "INSERT INTO Utilisateurs (nomUtilisateur, mdp, taille) VALUES (%s, %s, %s);"
		print(self.sql(sql, [name, password, height, is_student]))
		self.save()

	def add_movement_data(self, idUser, idDispositif, date, name):
		"""Ajoute un mouvement"""
		sql = "INSERT INTO DonneesMouvements (idUtilisateur, idDispositif, date, nom) VALUES (%s, %s, %s, %s);"
		self.sql(sql, [idUser, idDispositif, date, name])
		self.save()


	def last_user_id(self):
		return self.sql("SELECT idUtilisateur FROM Utilisateurs ORDER BY idUtilisateur DESC LIMIT 1")[0][0]

db = Database()