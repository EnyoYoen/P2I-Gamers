from database import*
from datetime import datetime
import time
from dataclass import *
import secret
import mysql.connector as mysql

db = Database()
db.connexion()
liste = db.list_mouvements_info()
print(liste)

id_max = -1
for row in liste:
    id = row.idMvt
    if id>id_max:
        id_max = id

id_mvt = id_max + 1

connexion = db.connexion()
cursor = connexion.cursor()
cursor.execute("INSERT INTO DonneesMouvements (idDonneeMouvement) VALUES (id_mvt);")
connexion.commit()

data = (idDispositif, date, name)
db.add_movement_data(idDispositif=1,date=123123,name=test)
    
