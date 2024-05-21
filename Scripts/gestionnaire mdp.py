import hashlib
import database

def calculate_sha256(data):
    # Convertit data en bites si ce n'est pas déjà le cas
    if isinstance(data, str):
        data = data.encode()

    # Calcule le SHA-256 hash
    sha256_hash = hashlib.sha256(data).hexdigest()

    return sha256_hash


def enregistrer_user(idUser):
    use = db.get_user(idUser)
    mdp = use.password
    h_mdp = calculate_sha256(mdp)

    use.password = h_mdp
    # db.add_user(use.idUtilisateur, h_mdp, use.taille)


def verifier_user(idUser):
    mdp = db.get_user(idUser).password

    mdp_ut = input("mot de passe: ")
    h_mdp_ut = calculate_sha256(mdp_ut)
    
    if h_mdp_ut == mdp:
        verif = True
    else:
        verif = False

    return verif

