class DataClass:
	KEYS: list = ...

	@classmethod
	def from_raw(cls, data):
		out = cls()
		for k, v in zip(out.KEYS, data):
			setattr(out, k, v)

		return out

	@classmethod
	def from_raw_list(cls, data):
		out = []
		if data is not None:
			for row in data:
				out.append(cls.from_raw(row))
		return out

	@classmethod
	def cast(cls, func):
		def wrapper(*args, **kwargs):
			out = func(*args, **kwargs)
			return cls.from_raw_list(out)
		return wrapper

	@classmethod
	def cast_single(cls, func):
		def wrapper(*args, **kwargs):
			out = func(*args, **kwargs)
			return cls.from_raw(out)
		return wrapper

	def __repr__(self):
		return '{' + ', '.join(map(lambda k: f'{k}: {getattr(self, k)}', self.KEYS)) + '}'

class MouvementInfo(DataClass):
	KEYS = [
		'idMvt',
		'nom',
		'dateCreation',
		'idUtilisateur' # qui a créé le mouvement
	]

class MesureSimple(DataClass):
	KEYS = [
		'idCapteur',
		'idMesure',
		'dateCreation',
		'valeur',
		'idPaquet',
		'idMvt'
	]

class MesureVect(DataClass):
	KEYS = [
		'idCapteur',
		'idMesure',
		'dateCreation',
		'X',
		'Y',
		'Z',
		'idPaquet',
		'idMvt'
	]

class Capteur(DataClass):
	KEYS = [
		'idCapteur',
		'type',
		'nom',
		'fabricant',
		'date_installation',
		'date_desinstallation'
	]
 
class Paquet(DataClass):
	KEYS = [
		'idPaquet',
		'taille'
	]

class Utilisateur(DataClass):
	KEYS = [
		'idUtilisateur',
		'username',
		'password',
		'taille',
		'age',
		'poids'
	]