from database import *
from datetime import datetime, timedelta
import time
from dataclass import *
import secret
import mysql.connector as mysql

db = Database()
db.connexion()

def register(date:datetime, nomMouvement, idUser, idDispositif):
    date_sql = date.strftime('%Y-%m-%d %H:%M:%S')
    date_end = date + timedelta(hours = 30)
    date_sql_end = date_end.strftime('%Y-%m-%d %H:%M:%S')

    
    sql = "SELECT date FROM MesuresSimples WHERE date >= %s AND date < %s"
    val = db.sql(sql, [date_sql, date_sql_end]) 

    mvmt = [val[0][0]]
    for i in range(len(val)-1):
        if val[i+1][0] - val[1][0] < timedelta(seconds=10):
            mvmt.append(val[i+1][0])

    
    sql = "SELECT date FROM MesuresVect WHERE date >= %s AND date < %s"
    val_v = db.sql(sql, [date_sql, date_sql_end]) 

    mvmt_v = [val_v[0][0]]
    for i in range(len(val_v)-1):
        if val_v[i+1][0] - val_v[1][0] < timedelta(minutes=15):
            mvmt_v.append(val_v[i+1][0])
    

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db.add_movement_data(idUser, idDispositif, now, nomMouvement)

    sql = "SELECT idDonneeMouvement FROM DonneesMouvements WHERE nom=%s AND date=%s"
    idDonneeMouvement = db.sql(sql, [nomMouvement, now])

    sql = "UPDATE MesuresSimples SET idDonneeMouvement = %s WHERE date>=%s AND date<=%s"
    db.sql(sql, [idDonneeMouvement[0][0], mvmt[0], mvmt[-1]])

    sql = "UPDATE MesuresVect SET idDonneeMouvement = %s WHERE date>=%s AND date<=%s"
    db.sql(sql, [idDonneeMouvement[0][0], mvmt_v[0], mvmt_v[-1]])

    db.save()

# register(datetime(2024, 5, 21, 10, 43, 32), "test", 10, 1)



