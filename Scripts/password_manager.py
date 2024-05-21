import hashlib
from database import Database

db = Database()

def calculate_sha256(data):
    # Convertit data en bites si ce n'est pas déjà le cas
    if isinstance(data, str):
        data = data.encode()

    # Calcule le SHA-256 hash
    sha256_hash = hashlib.sha256(data).hexdigest()

    return sha256_hash


def register_user(name, password, height):
    liste = db.list_users()
    for i in liste.name:
        if i == name:
            return False
    h_mdp = calculate_sha256(password)
    db.add_user(name, h_mdp, height)
    return True


def verify_user(idUser: str, mdp_ut: str) -> bool:

    mdp = db.get_user(idUser).password
    h_mdp_ut = calculate_sha256(mdp_ut)
    
    if h_mdp_ut == mdp:
        verif = True
    else:
        verif = False

    return verif

