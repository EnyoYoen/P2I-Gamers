from datetime import datetime
import time
from dataclass import *
import secret
import mysql.connector as mysql


class Database:
	"""Gestion de la base de donnée"""
	def __init__(self):
		self.connexion_bd = None
		# self.connexion()
		
	def connexion(self):
		try:
			self.connexion_bd = mysql.connect(**secret.DATABASE_LOGIN)
			print(f"=> Connexion à {secret.DATABASE_LOGIN['database']} établie...")
		except Exception as e:
			print('MySQL [CONNEXION ERROR]')
			print(e)
		return self.connexion_bd

	def sql(self, sql, params=None):
		return []
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
		sql = "SELECT * FROM DonneesMouvements WHERE idUtilisateur=%s" 
		return self.sql(sql, [id_user])

	@MouvementInfo.cast_single
	def get_mouvements_info(self, idDonneeMouvement):
		"""Renvoie les infos associees a un mouvement idDonneeMouvement"""
		sql = "SELECT * FROM DonneesMouvements WHERE idDonneeMouvement=%s"
		return self.sql(sql, [idDonneeMouvement])[0]

	@MesureSimple.cast
	def get_mesure_simple(self, idDonneeMouvement):
		"""Renvoie la liste de mesures simples correspondant au mouvement idDonneeMouvement"""
		sql = "SELECT * FROM MesuresSimples WHERE idDonneeMouvement = %s"
		return self.sql(sql, [idDonneeMouvement])

	@MesureVect.cast
	def get_mesure_vect(self, idDonneeMouvement):
		"""Renvoie la liste de mesures vectorielles correspondant au mouvement idDonneeMouvement"""
		sql = "SELECT * FROM MesuresVect WHERE idDonneeMouvement = %s"
		return self.sql(sql, [idDonneeMouvement])

	def get_mouvement(self, idDonneeMouvement):
		"""Renvoie toutes les données associées à idDonneeMouvement"""
		return self.get_mouvements_info(idDonneeMouvement), self.get_mesure_simple(idDonneeMouvement), self.get_mesure_vect(idDonneeMouvement)

	@Capteur.cast
	def list_capteurs(self):
		"""Renvoie la liste des capteurs"""
		sql = "SELECT * FROM Capteurs"
		return self.sql(sql)

	@Capteur.cast_single
	def get_capteur(self, idCapteur):
		"""Renvoie le capteur correspondant à idCapteur"""
		sql = "SELECT c.*, tc.nomCapteur, tc.fabricant, tc.TypeCapteur FROM Capteurs c, TypeCapteur tc WHERE idCapteur=%s and c.idPlacement=tc.idPlacement"
		return self.sql(sql, [idCapteur])[0]
	
	@Capteur.cast
	def list_type_capteurs(self):
		"""Renvoie la liste des types de capteurs"""
		sql = "SELECT * FROM Typecapteur"
		return self.sql(sql)

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
		v = ", ".join(["(%s, %s, %s, %s, %s, %s)"] * len(vects))
		sql = "INSERT INTO MesuresVect (idCapteur, idDonneeMouvement, date, x, y, z) VALUES " + v
		data = []
		for vect in vects:
			data.extend(vect)
		self.sql(sql, data)

		v = ", ".join(["(%s, %s, %s, %s)"] * len(simples))
		sql = "INSERT INTO MesuresSimples (idCapteur, idDonneeMouvement, date, valeur) VALUES " + v
		data = []
		for simple in simples:
			data.extend(simple)
		self.sql(sql, data)

		if save:
			self.save()

	def add_user(self, name, password, height, is_student):
		"""Ajoute un utilisateur"""
		sql = "INSERT INTO Utilisateurs (nomUtilisateur, mdp, taille, eleve) VALUES (%s, %s, %s, %s);"
		print(self.sql(sql, [name, password, height, is_student]))
		self.save()

	def add_movement_data(self, idUser, idDispositif, date, name):
		"""Ajoute un mouvement et renvoie l'idMvmt correspondant."""
		sql = f'SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = "{secret.DATABASE_LOGIN["database"]}" AND TABLE_NAME = "DonneesMouvements";'
		# La valeur vient de secret, si quelqu'un l'a modifié alors il a acces aux mdp donc c'est safe.

		value = self.sql(sql)
		if not value or not value[0][0]:
			# Shouldn't happen?
			idMvmt = 0
		else:
			idMvmt = value[0][0]

		sql = "INSERT INTO DonneesMouvements (idDonneeMouvement, idUtilisateur, idDispositif, date, nom) VALUES (%s, %s, %s, %s, %s);"
		self.sql(sql, [idMvmt, idUser, idDispositif, date, name])
		# TODO - Gérer les collisions, si deux utilisateurs tentent d'enregistrer un mouvement en meme temps on pourrait alors avoir un problème sur la contrainte unique id

		self.save()

		return idMvmt

	def rename_donnees(self, idMvt, name, save=True):
		sql = "UPDATE DonneesMouvements SET idUtilisateur=1, nom=%s WHERE idDonneeMouvement=%s"
		self.sql(sql, [name, idMvt])
		if save:
			self.save()

	def last_user_id(self):
		return self.sql("SELECT idUtilisateur FROM Utilisateurs ORDER BY idUtilisateur DESC LIMIT 1")[0][0]

db = Database()