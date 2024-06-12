# -*- coding: utf-8 -*-
"""
Created on Tue May 14 08:53:00 2024

@author: giaho
"""
from dataclass import MesureVect,MesureSimple   
import numpy as np
from random import randint
import matplotlib.pyplot as plt
from math import sqrt, acos, asin, atan
from database import Database as db
from datetime import datetime, timedelta


def interpolation_vect(mvt_exp, mvt_th):
    inter = []
    j = 0
    for i in range(0,len(mvt_exp)):
        t1_th = mvt_th[j].dateCreation
        t1 = mvt_exp[i].dateCreation
        x1 = mvt_exp[i].X
        y1 = mvt_exp[i].Y
        z1 = mvt_exp[i].Z
        # print(t1)
        # print(t1_th)
        if t1_th == t1:
            inter.append(MesureVect.from_raw((0,0,0,t1,x1,y1,z1)))
            # print(f"valeur gardée : {(t1,x1,y1,z1)}")
            j += 1
        else:
            while t1_th < t1:
                t1_th = mvt_th[j].dateCreation
                x2 = mvt_exp[i-1].X
                y2 = mvt_exp[i-1].Y
                z2 = mvt_exp[i-1].Z
                t = t1_th
                x = (x1 + x2)/2
                y = (y1 + y2)/2
                z = (z1 + z2)/2
                inter.append(MesureVect.from_raw((0,0,0,t,x,y,z)))
                j += 1
                t1_th = mvt_th[j].dateCreation
                # print(f"valeur ajoutée : {(t,x,y,z)}")
            inter.append(MesureVect.from_raw((0,0,0,t1_th,x1,y1,z1)))
            # print(f"valeur gardée : {(t1_th,v)}")
            j += 1        
    inter.sort(key=lambda e: e.dateCreation)
    return inter

def interpolation_simple(mvt_exp, mvt_th):
    inter = []
    j = 0
    # print(len(mvt_th))
    # print(len(mvt_exp))
    for i in range(0,len(mvt_exp)):
        t1_th = mvt_th[j].dateCreation
        t1 = mvt_exp[i].dateCreation
        v1 = mvt_exp[i].valeur
        # print(t1)
        # print(t1_th)
        if t1_th == t1:
            inter.append(MesureSimple.from_raw((0,0,t1,v1)))
            # print(f"valeur gardée : {(t1,v1)}")
            j += 1
        else:
            while t1_th < t1:
                if j == (len(mvt_th)-2):
                    break
                t1_th = mvt_th[j].dateCreation
                v2 = mvt_exp[i-1].valeur
                t = t1_th
                v = (v1 + v2)/2
                # print(v)
                inter.append(MesureSimple.from_raw((0,0,t,v)))
                j += 1
                t1_th = mvt_th[j].dateCreation
                # print(f"valeur ajoutée : {(t,v)}")
                if j == (len(mvt_th)-2):
                    break
                
            inter.append(MesureSimple.from_raw((0,0,t1_th,v1)))
            # print(f"valeur gardée : {(t1_th,v1)}")
            j += 1  
    inter.sort(key=lambda e: e.dateCreation)
    return inter

# def derivee(liste):
#     drv = []
#     for i in range(len(liste)-1):
#         x1 = liste[i].X
#         y1 = liste[i].Y
#         z1 = liste[i].Z  
#         t1 = liste[i].dateCreation  
#         x2 = liste[i+1].X
#         y2 = liste[i+1].Y
#         z2 = liste[i+1].Z
#         t2 = liste[i+1].dateCreation
#         dt =  t2 - t1
#         dx = (x2 - x1)/dt
#         dy = (y2 - y1)/dt
#         dz = (z2 - z1)/dt
#         drv.append((0,0,dt,dx,dy,dz))
#     return drv

def formatageS(dico, mesures_simple):
    debut  = mesures_simple[0].dateCreation
    for mvt in mesures_simple:
        dt = mvt.dateCreation
        delta = (dt-debut)
        if mvt.idCapteur > 5:
            dico["Flexion"].append(MesureSimple.from_raw((0,0,delta.total_seconds(), mvt.valeur)))
        if mvt.idCapteur <= 5:
            dico["FlexiForce"].append(MesureSimple.from_raw((0,0,delta.total_seconds(), mvt.valeur)))
    return dico

def formatageV(dico,mesures_vect):
    debut  = mesures_vect[0].dateCreation
    for mvt in mesures_vect:
        dt = mvt.dateCreation
        delta = (dt - debut)
        dico["Centrale inertielle"].append(MesureVect.from_raw((0,0,delta.total_seconds(), mvt.X, mvt.Y, mvt.Z)))
    return dico

def formatageS_exp(dico, mesures_simple):
    debut  = mesures_simple[0].dateCreation
    for mvt in mesures_simple:
        dt = mvt.dateCreation
        delta = (dt-debut)
        d = datetime.now().timestamp() - 4
        if mvt.idCapteur > 5:
            if dt.timestamp() >= d:
                dico["Flexion"].append(MesureSimple.from_raw((0,0,delta.total_seconds(), mvt.valeur)))
        if mvt.idCapteur <= 5:
            if dt.timestamp() >= d:
                dico["FlexiForce"].append(MesureSimple.from_raw((0,0,delta.total_seconds(), mvt.valeur)))
    return dico

def formatageV_exp(dico,mesures_vect):
    debut  = mesures_vect[0].dateCreation
    fin = mesures_vect[-1].dateCreation
    for mvt in mesures_vect:
        dt = mvt.dateCreation
        delta = (dt - debut)
        d = datetime.now().timestamp() - 4
        if dt.timestamp() >= d:
            dico["Centrale inertielle"].append(MesureVect.from_raw((0,0,delta.total_seconds(), mvt.X, mvt.Y, mvt.Z)))
    return dico

def formatageS_exptot(dico, mesures_simple):
    debut  = mesures_simple[0].dateCreation
    for mvt in mesures_simple:
        dt = mvt.dateCreation
        delta = (dt-debut)
        if mvt.idCapteur > 5:
            dico["Flexion"].append(MesureSimple.from_raw((0,0,delta.total_seconds(), mvt.valeur)))
        if mvt.idCapteur <= 5:
            dico["FlexiForce"].append(MesureSimple.from_raw((0,0,delta.total_seconds(), mvt.valeur)))
    return dico

def formatageV_exptot(dico,mesures_vect):
    debut  = mesures_vect[0].dateCreation
    for mvt in mesures_vect:
        dt = mvt.dateCreation
        delta = (dt - debut)
        dico["Centrale inertielle"].append(MesureVect.from_raw((0,0,delta.total_seconds(), mvt.X, mvt.Y, mvt.Z)))
    return dico

def comparaison_direct2(mesures_simple,mesures_vect, idMvt):  
    data = ['FlexiForce', 'Flexion', 'Centrale inertielle']
    mvt_info, mesures_simple_th, mesures_vect_th = db().get_mouvement(idMvt)

    dico_th = {}
    dico_th["FlexiForce"] = []
    dico_th["Flexion"] = []
    dico_th["Centrale inertielle"] = []
    dico_th = formatageS(dico_th, mesures_simple_th)
    dico_th = formatageV(dico_th, mesures_vect_th)

    taux = []
    box = {}

    dico_exp = {}
    dico_exp["FlexiForce"] = []
    dico_exp["Flexion"] = []
    dico_exp["Centrale inertielle"] = []
    dico_exp = formatageS_exp(dico_exp, mesures_simple)
    dico_exp = formatageV_exp(dico_exp, mesures_vect)
    print(dico_th["Flexion"])
    print(dico_exp["Flexion"])
    
    for type in data:
        mvt_exp = dico_exp[type]
        err_i = 100
        res = []
        mvt_exp_inter = []
        ti = mvt_exp[0].dateCreation
        print(mvt_exp)
        tf = mvt_exp[-1].dateCreation
        mvt_th = dico_th[type]
        mvt_th_compare = []  
        i = 0
        
        if isinstance(mvt_th[i].dateCreation, timedelta):
            mvt_th[i].dateCreation = mvt_th[i].dateCreation.total_seconds()
        
        while mvt_th[i].dateCreation < ti :
            i += 1
        while ti < mvt_th[i].dateCreation < tf:
            mvt_th_compare.append(mvt_th[i])
            i += 1
        if type == 'Centrale inertielle':
            # mvt_exp_inter = interpolation_vect(mvt_exp, mvt_th_compare)
            # mvt_exp = mvt_exp_inter
            err_teta = []
            box["teta"] = err_teta
            err_phi = []
            box["phi"] = err_phi
            if mvt_exp != 0 :  
                for i in range(len(mvt_exp)):
                    delta = 1e-10
                    x1 = float(mvt_th[i].X)+delta
                    y1 = float(mvt_th[i].Y)+delta
                    z1 = float(mvt_th[i].Z)+delta
                    x2 = float(mvt_exp[i].X)
                    y2 = float(mvt_exp[i].Y)
                    z2 = float(mvt_exp[i].Z)

                    r2 = sqrt((x2**2)+(y2**2)+(z2**2))
                    teta2 = acos(z2/r2)
                    phi2 = atan(y2/x2)
                    r1 = sqrt((x1**2)+(y1**2)+(z1**2))
                    # print(r1)
                    teta1 = acos(z1/r1)
                    phi1 = atan(y1/x1)
                    err_t = 100*abs(teta1-teta2)/teta1
                    err_p = 100*abs(phi1-phi2)/phi1
                    err_teta.append(err_t)
                    err_phi.append(err_p)

                    err_x = 100*abs(x1-x2)/x1
                    err_y = 100*abs(y1-y2)/y1
                    err_z = 100*abs(z1-z2)/z1
                    moy = (err_x + err_y + err_z)/3
                    res.append(moy)  
                err_f = np.mean(res)
                if err_f < err_i:
                    err_i = err_f
                # else:
                #     return taux, box
            resultat = 100-err_i
            resultat = round(resultat, 2)
            taux.append(float(resultat))
        
        elif type == 'FlexiForce':
            # mvt_exp_inter = interpolation_simple(mvt_exp, mvt_th_compare)
            # mvt_exp = mvt_exp_inter
            err_pression = []
            box["pression"] = err_pression
            j = 0
            if mvt_exp != 0 :   
                for i in range(len(mvt_exp)):
                    v1 = mvt_th[i].valeur    
                    v2 = mvt_exp[i].valeur
                    err = 100*abs(v1-v2)
                    err_pression.append(err)
                    res.append(err)  
                    j =+1 
                err_f = np.mean(res) 
                if err_f < err_i:
                    err_i = err_f
            resultat = 100-err_i
            resultat = round(resultat, 2)
            taux.append(float(resultat))

        else:
            # mvt_exp_inter = interpolation_simple(mvt_exp, mvt_th_compare)
            # mvt_exp = mvt_exp_inter
            err_flexion = []
            box["flexion"] = err_flexion
            j = 0
            if mvt_exp != 0 :   
                for i in range(len(mvt_exp)):
                    v1 = mvt_th[i].valeur    
                    v2 = mvt_exp[i].valeur
                    err = 100*abs(v1-v2)
                    res.append(err) 
                    err_flexion.append(err)  
                    j += 1
                err_f = np.mean(res) 
                if err_f < err_i:
                    err_i = err_f
            resultat = 100-err_i
            resultat = round(resultat, 2)
            taux.append(float(resultat))
        # print(taux)
        erreur = np.mean(taux)
    return erreur, box

def comparaison_direct(dico_th, dico_exp):  
    data = ['FlexiForce', 'Flexion', 'Centrale inertielle']
    # dico_th = dico_total[nom]
    taux = []
    box = {}
    
    for type in data:
        mvt_exp = dico_exp[type]
        err_i = 100
        res = []
        mvt_exp_inter = []
        ti = mvt_exp[0].dateCreation
        tf = mvt_exp[-1].dateCreation
        mvt_th = dico_th[type]
        mvt_th_compare = []  
        i = 0
        if ti != 0:
            while mvt_th[i].dateCreation < ti :
                i += 1
            while ti <= mvt_th[i].dateCreation <= tf:
                mvt_th_compare.append(mvt_th[i])
                i += 1
            if type == 'Centrale inertielle':
                mvt_exp_inter = interpolation_vect(mvt_exp, mvt_th_compare)
                mvt_exp = mvt_exp_inter
                err_teta = []
                box["teta"] = err_teta
                err_phi = []
                box["phi"] = err_phi
                if mvt_exp != 0 :  
                    for i in range(len(mvt_exp)):
                        x1 = mvt_th_compare[i].X
                        y1 = mvt_th_compare[i].Y
                        z1 = mvt_th_compare[i].Z    
                        x2 = mvt_exp[i].X
                        y2 = mvt_exp[i].Y
                        z2 = mvt_exp[i].Z

                        r2 = sqrt((x2**2)+(y2**2)+(z2**2))
                        teta2 = acos(z2/r2)
                        phi2 = atan(y2/x2)
                        r1 = sqrt((x1**2)+(y1**2)+(z1**2))
                        teta1 = acos(z1/r1)
                        phi1 = atan(y1/x1)
                        err_t = 100*abs(teta1-teta2)/teta1
                        err_p = 100*abs(phi1-phi2)/phi1
                        err_teta.append(err_t)
                        err_phi.append(err_p)

                        err_x = 100*abs(x1-x2)/x1
                        err_y = 100*abs(y1-y2)/y1
                        err_z = 100*abs(z1-z2)/z1
                        moy = (err_x + err_y + err_z)/3
                        res.append(moy)  
                    err_f = np.mean(res)
                    if err_f < err_i:
                        err_i = err_f
                    # else:
                    #     return taux, box
                resultat = 100-err_i
                resultat = round(resultat, 2)
                taux.append(resultat)
            
            elif type == 'FlexiForce':
                mvt_exp_inter = interpolation_simple(mvt_exp, mvt_th)
                mvt_exp = mvt_exp_inter
                err_pression = []
                box["pression"] = err_pression
                if mvt_exp_inter != 0 :   
                    for i in range(len(mvt_exp)):
                        v1 = mvt_th[i].valeur    
                        v2 = mvt_exp[i].valeur
                        err = 100*abs(v1-v2)
                        err_pression.append(err)
                        res.append(err)   
                    err_f = np.mean(res) 
                    if err_f < err_i:
                        err_i = err_f
                resultat = 100-err_i
                resultat = round(resultat, 2)
                taux.append(resultat)

            else:
                mvt_exp_inter = interpolation_simple(mvt_exp, mvt_th_compare)
                mvt_exp = mvt_exp_inter
                err_flexion = []
                box["flexion"] = err_flexion
                if mvt_exp_inter != 0 :   
                    for i in range(len(mvt_exp)):
                        v1 = mvt_th_compare[i].valeur    
                        v2 = mvt_exp[i].valeur
                        err = 100*abs(v1-v2)
                        res.append(err) 
                        err_flexion.append(err)  
                    err_f = np.mean(res) 
                    if err_f < err_i:
                        err_i = err_f
                resultat = 100-err_i
                resultat = round(resultat, 2)
                taux.append(resultat)
        erreur = np.mean(taux)
    return erreur, box

def comparaison_total(id_th, mesures_simple, mesures_vect):
    data = ['FlexiForce', 'Flexion', 'Centrale inertielle']
    reponse = f'Le geste a été effectué avec :'
    box ={}
    mvt_info, mesures_simple_th, mesures_vect_th = db().get_mouvement(id_th)

    dico_th = {}
    dico_th["FlexiForce"] = []
    dico_th["Flexion"] = []
    dico_th["Centrale inertielle"] = []
    dico_th = formatageS(dico_th, mesures_simple_th)
    dico_th = formatageV(dico_th, mesures_vect_th)

    dico_exp = {}
    dico_exp["FlexiForce"] = []
    dico_exp["Flexion"] = []
    dico_exp["Centrale inertielle"] = []
    dico_exp = formatageS_exptot(dico_exp, mesures_simple)
    dico_exp = formatageV_exptot(dico_exp, mesures_vect)

    # print(dico_th)
    # print(dico_exp)

    for type in data:
        mvt_exp = dico_exp[type]
        err_i = 100
        res = []
        # mvt_exp_inter = []
        mvt_th = dico_th[type]
        duree_th = mvt_th[-1].dateCreation - mvt_th[0].dateCreation
        duree_exp = mvt_exp[-1].dateCreation - mvt_exp[0].dateCreation
        r = duree_exp/duree_th
        for row in mvt_exp:
            t = round(row.dateCreation/r)
            row.dateCreation = t       

        # print(len(mvt_exp))
        # print(len(mvt_th))

        len_mvt = len(mvt_th)
        if len(mvt_exp) < len(mvt_th):
            len_mvt = len(mvt_exp)   

        # print(len_mvt)     
        
        if type == 'Centrale inertielle':
            # mvt_exp_inter = interpolation_vect(mvt_exp, mvt_th)
            # mvt_exp = mvt_exp_inter
            err_teta = []
            box["teta"] = err_teta
            err_phi = []
            box["phi"] = err_phi
            if mvt_exp != [] :  
                for i in range(len_mvt):
                    epi = 10**(-11)
                    x1 = float(mvt_th[i].X) + epi
                    y1 = float(mvt_th[i].Y) + epi
                    z1 = float(mvt_th[i].Z) + epi
                    x2 = float(mvt_exp[i].X) + epi
                    y2 = float(mvt_exp[i].Y) + epi
                    z2 = float(mvt_exp[i].Z) + epi


                    r2 = sqrt((x2**2)+(y2**2)+(z2**2))
                    teta2 = acos(z2/r2)
                    phi2 = atan(y2/x2)
                    r1 = sqrt((x1**2)+(y1**2)+(z1**2))
                    teta1 = acos(z1/r1)
                    phi1 = atan(y1/x1)
                    err_t = 100*abs(teta1-teta2)/teta1
                    err_p = 100*abs(phi1-phi2)/phi1
                    err_teta.append(err_t)
                    err_phi.append(err_p)

                    err_x = 100*abs(x1-x2)/x1
                    err_y = 100*abs(y1-y2)/y1
                    err_z = 100*abs(z1-z2)/z1
                    moy = (err_x + err_y + err_z)/3
                    # res.append(moy) 
                err_f1 = np.mean(err_teta)
                err_f2 = np.mean(err_phi)
                if err_f1 < err_i and err_f2 < err_i:
                    err_i1 = err_f1
                    err_i2 = err_f2
                else:
                    text = "trop d'erreurs en positions."
                    reponse += text
                    return reponse
            resultat1 = 100-err_i1
            resultat2 = 100-err_i2
            resultat1 = round(resultat1, 2)
            resultat2 = round(resultat2, 2)
            text = f' {resultat1}% en teta et {resultat2}% de réussite en phi'  
            reponse += text
        
        elif type == 'FlexiForce':
            # mvt_exp_inter = interpolation_simple(mvt_exp, mvt_th)
            # mvt_exp = mvt_exp_inter
            err_pression = []
            box["pression"] = err_pression
            if mvt_exp != [] :   
                for i in range(len_mvt):
                    v1 = mvt_th[i].valeur    
                    v2 = mvt_exp[i].valeur
                    err = 100*abs(v1-v2)
                    err_pression.append(err)
                    res.append(err)   
                err_f = np.mean(res) 
                if err_f < err_i:
                    err_i = err_f
                else:
                    text = "trop d'erreurs, recommencer."
            else:
                text = "Aucun mouvement enregistré, recommencer."
                reponse += text
                return reponse
            resultat = 100-err_i
            resultat = round(resultat, 2)
            text = f' {resultat}% de réussite en pression,'
            reponse += text 
        else:
            # mvt_exp_inter = interpolation_simple(mvt_exp, mvt_th)
            # mvt_exp = mvt_exp_inter
            err_flexion = []
            box["flexion"] = err_flexion
            if mvt_exp != [] :   
                for i in range(len_mvt):
                    v1 = mvt_th[i].valeur    
                    v2 = mvt_exp[i].valeur
                    err = 100*abs(v1-v2)
                    err_flexion.append(err)
                    res.append(err)   
                err_f = np.mean(res) 
                if err_f < err_i:
                    err_i = err_f
                else:
                    text = "trop d'erreurs, recommencer."
            else:
                text = "Aucun mouvement enregistré, recommencer."
                reponse += text
                return reponse
            resultat = 100-err_i
            resultat = round(resultat, 2)
            text = f' {resultat}% de réussite en flexion,'
            reponse += text
    return reponse


if __name__ == "__main__":
    mvt_exp = {'FlexiForce': MesureSimple.from_raw_list([(0,0,10,0),(0,0,13,0),(0,0,15,0)]),
               'Flexion': MesureSimple.from_raw_list([(0,0,10,4),(0,0,13,5),(0,0,15,5)]), 
               'Centrale inertielle': MesureVect.from_raw_list([(0,0,0,10,9,8,4),(0,0,0,13,3,2,3),(0,0,0,15,10,8,1)])}

    mvt_exp2 = {'FlexiForce' : MesureSimple.from_raw_list([(0, 0, 0, 0),(0, 0, 1, 0), (0, 0, 2, 0), (0, 0, 3, 0), (0, 0, 4, 0),
                                        (0, 0, 5, 1), (0, 0, 6, 1), (0, 0, 7, 0), (0, 0, 8, 1), (0, 0, 9, 0), (0, 0, 10, 0), 
                                        (0, 0, 11, 0), (0, 0, 12, 1), (0, 0, 13, 0), (0, 0, 14, 0), (0, 0, 15, 0), (0, 0, 16, 0)]),
                    'Flexion': MesureSimple.from_raw_list([(0, 0, 0, 0),(0, 0, 1, 4), (0, 0, 2, 2), (0, 0, 3, 4), (0, 0, 4, 2), (0, 0, 5, 3), 
                                        (0, 0, 6, 2), (0, 0, 7, 3), (0, 0, 8, 4), (0, 0, 9, 3), (0, 0, 10, 4), (0, 0, 11, 4), 
                                        (0, 0, 12, 5), (0, 0, 13, 5), (0, 0, 14, 3), (0, 0, 15, 5), (0, 0, 16, 3)]),
                    'Centrale inertielle': MesureVect.from_raw_list([(0, 0, 0, 0, 3, 9, 9), (0, 0, 0, 1, 3, 9, 9), (0, 0, 0, 2, 4, 6, 8), 
                                        (0,0, 0, 3, 10, 1, 4), (0,0, 0, 4, 5, 5, 7), (0,0, 0, 5, 7, 6, 10), (0,0, 0, 6, 8, 2, 5), 
                                        (0,0, 0, 7, 6, 4, 4), (0,0, 0, 8, 2, 3, 2), (0,0, 0, 9, 10, 2, 9), (0,0, 0, 10, 9, 8, 4), 
                                        (0,0, 0, 11, 2, 9, 1), (0,0, 0, 12, 10, 4, 4), (0,0, 0, 13, 3, 2, 3), (0,0, 0, 14, 9, 1, 5), 
                                        (0,0, 0, 15, 10, 8, 1),(0,0, 0, 16, 4, 8, 1)])}
    
    data_th = {'FlexiForce' : MesureSimple.from_raw_list([(0, 0, 0, 0),(0, 0, 1, 0), (0, 0, 2, 0), (0, 0, 3, 0), (0, 0, 4, 0),
                                        (0, 0, 5, 1), (0, 0, 6, 1), (0, 0, 7, 0), (0, 0, 8, 1), (0, 0, 9, 0), (0, 0, 10, 0), 
                                        (0, 0, 11, 0), (0, 0, 12, 1), (0, 0, 13, 0), (0, 0, 14, 0), (0, 0, 15, 0), (0, 0, 16, 0)]),
                    'Flexion': MesureSimple.from_raw_list([(0, 0, 0, 0),(0, 0, 1, 4), (0, 0, 2, 2), (0, 0, 3, 4), (0, 0, 4, 2), (0, 0, 5, 3), 
                                        (0, 0, 6, 2), (0, 0, 7, 3), (0, 0, 8, 4), (0, 0, 9, 3), (0, 0, 10, 4), (0, 0, 11, 4), 
                                        (0, 0, 12, 5), (0, 0, 13, 5), (0, 0, 14, 3), (0, 0, 15, 5), (0, 0, 16, 3)]),
                    'Centrale inertielle': MesureVect.from_raw_list([(0,0, 0, 0, 3, 9, 9), (0,0, 0, 1, 3, 9, 9), (0,0, 0, 2, 4, 6, 8), 
                                        (0,0, 0, 3, 10, 1, 4), (0,0, 0, 4, 5, 5, 7), (0,0, 0, 5, 7, 6, 10), (0,0, 0, 6, 8, 2, 5), 
                                        (0,0, 0, 7, 6, 4, 4), (0,0, 0, 8, 2, 3, 2), (0,0, 0, 9, 10, 2, 9), (0,0, 0, 10, 9, 8, 4), 
                                        (0,0, 0, 11, 2, 9, 1), (0,0, 0, 12, 10, 4, 4), (0,0, 0, 13, 3, 2, 3), (0,0, 0, 14, 9, 1, 5), 
                                        (0,0, 0, 15, 10, 8, 1),(0,0, 0, 16, 4, 8, 1)])}
    
    # test :
    # erreur , box1 = comparaison_direct(data_th, mvt_exp)   
    # print(erreur)
    
    mvmt_info, mesures_simple, mesures_vect = db().get_mouvement(322)
    texte = comparaison_total(323, mesures_simple, mesures_vect)   
    print(texte)
    
    # my_dict = box1
    # plt.boxplot(my_dict.values(), labels=my_dict.keys())
    # plt.show()
    
    

    # mvmt_info, mesures_simple, mesures_vect = db().get_mouvement(390)

    # err, box = comparaison_direct2(mesures_simple,mesures_vect, 329)
    # print(err)