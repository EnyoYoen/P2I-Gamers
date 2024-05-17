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
	def list_mouvements_info(self):
		"""Renvoie la liste de tous les mouvements preenregistres"""
		sql = "SELECT * FROM Mouvements" # TODO !!
		return self.sql(sql)

	@MouvementInfo.cast_single
	def get_mouvements_info(self, idMouvement):
		"""Renvoie les infos associees a un mouvement idMouvement"""
		sql = "SELECT * FROM Mouvements WHERE idMouvement=%s"
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


	def add_paquet(self, size):
		"""Ajoute un paquet de taille size"""
		sql = "INSERT INTO Paquets (taille) VALUES (%s)"
		self.sql(sql, [size])
		self.save()

	def add_sensor_type(self, type, manufacturer, name):
		"""Ajoute un type de capteur"""
		sql = "INSERT INTO TypeCapteurs (type, fabricant, nom) VALUES (%s, %s, %s)"
		self.sql(sql, [type, manufacturer, name])
		self.save()

	def add_sensor(self, idPlacement, idDispositif, installDate, uninstallDate = None):
		"""Ajoute un capteur"""
		if uninstallDate is None:
			sql = "INSERT INTO Capteurs (idPlacement, idDispositif, dateInstal) VALUES (%s, %s)"
			self.sql(sql, [idPlacement, idDispositif, installDate])
		else:	
			sql = "INSERT INTO Capteurs (idPlacement, idDispositif, dateInstal, dateDesinstal) VALUES (%s, %s, %s)"
			self.sql(sql, [idPlacement, idDispositif, installDate, uninstallDate])
		self.save()

	def add_contraption(self, name):
		"""Ajoute un dispositif"""
		sql = "INSERT INTO Dispositifs (nom) VALUES (%s)"
		self.sql(sql, [name])
		self.save()

	def add_mesure_simple(self, idCapteur, date, value, idPaquet, idDonneeMouvement):
		"""Ajoute une mesure simple"""
		sql = "INSERT INTO MesuresSimples (idCapteur, date, valeur, idPaquet, idDonneeMouvement) VALUES (%s, %s, %s, %s, %s)"
		self.sql(sql, [idCapteur, date, value, idPaquet, idDonneeMouvement])
		self.save()

	def add_mesure_vect(self, idCapteur, date, x, y, z, idPaquet, idDonneeMouvement):
		"""Ajoute une mesure vectorielle"""
		sql = "INSERT INTO MesuresVect (idCapteur, date, X, Y, Z, idPaquet, idDonneeMouvement) VALUES (%s, %s, %s, %s, %s, %s, %s)"
		self.sql(sql, [idCapteur, date, x, y, z, idPaquet, idDonneeMouvement])
		self.save()

	def add_user(self, name, password, height):
		"""Ajoute un utilisateur"""
		sql = "INSERT INTO Utilisateurs (nom, mdp, taille) VALUES (%s, %s, %s)"
		self.sql(sql, [name, password, height])
		self.save()

	def add_movement_data(self, idUser, idDisposition, date, name):
		"""Ajoute un mouvement"""
		sql = "INSERT INTO Mouvements (idUtilisateur, idDisposition, date, nom) VALUES (%s, %s, %s, %s)"
		self.sql(sql, [idUser, idDisposition, date, name])
		self.save()


if __name__ == "__main__":
	db = Database()
	a = db.list_mouvements_info()
	pass