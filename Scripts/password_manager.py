import hashlib
from database import Database

class PasswordManager:
	def __init__(self) -> None:
		self.db = Database()
	def calculate_sha256(self, data):
		# Convertit data en bites si ce n'est pas déjà le cas
		if isinstance(data, str):
			data = data.encode()

		# Calcule le SHA-256 hash
		sha256_hash = hashlib.sha256(data).hexdigest()

		return sha256_hash


	def register_user(self, name, password, height, is_student):
		liste = self.db.list_users()
		for i in liste:
			user = i.username
			if name == user:
				return False
		h_mdp = self.calculate_sha256(password)
		self.db.add_user(name, h_mdp, height, is_student)
		return self.db.last_user_id()


	def verify_user(self, idUser: str, mdp_ut: str) -> bool:

		user = self.db.get_user_by_name(idUser)
		mdp = user.password
		h_mdp_ut = self.calculate_sha256(mdp_ut)
		
		if h_mdp_ut == mdp:
			verif = True
		else:
			verif = False

		return None if not verif else user.idUtilisateur

