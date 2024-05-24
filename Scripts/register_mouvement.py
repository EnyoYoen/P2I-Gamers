from database import *
from datetime import datetime
import time
from dataclass import *
import secret
import mysql.connector as mysql

db = Database()
db.connexion()

def register(date:str):
    sql = "SELECT * FROM MesuresSimples WHERE date=%s"
    m = db.sql(sql, [date])
    mvt = [m]
    
    sql = "SELECT date FROM MesuresSimples WHERE date > %s"
    l_date = db.sql(sql, [date])
    print(l_date)

register("2024-05-21 10:43:32.000")



