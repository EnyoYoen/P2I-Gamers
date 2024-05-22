import hashlib
from database import db

def calculate_sha256(data):
    # Convertit data en bites si ce n'est pas déjà le cas
    if isinstance(data, str):
        data = data.encode()

    # Calcule le SHA-256 hash
    sha256_hash = hashlib.sha256(data).hexdigest()

    return sha256_hash


def register_user(name, password, height):
    liste = db.list_users()
    for i in liste:
        user = i.username
        if name == user:
            return False
    h_mdp = calculate_sha256(password)
    db.add_user(name, h_mdp, height)
    return db.last_user_id()


def verify_user(idUser: str, mdp_ut: str) -> bool:

    user = db.get_user_by_name(idUser)
    mdp = user.password
    h_mdp_ut = calculate_sha256(mdp_ut)
    
    if h_mdp_ut == mdp:
        verif = True
    else:
        verif = False

    return None if not verif else user.idUtilisateur

