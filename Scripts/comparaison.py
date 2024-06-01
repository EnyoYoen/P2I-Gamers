# -*- coding: utf-8 -*-
"""
Created on Tue May 14 08:53:00 2024

@author: giaho
"""
from dataclass import MesureVect,MesureSimple   
import numpy as np
from random import randint


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
            inter.append(MesureVect.from_raw((0,0,t1,x1,y1,z1)))
            # print(f"valeur gardée : {(0,0,t1,x1,y1,z1)}")
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
                inter.append(MesureVect.from_raw((0,0,t,x,y,z)))
                j += 1
                t1_th = mvt_th[j].dateCreation
                # print(f"valeur ajoutée : {(0,0,t,x,y,z)}")
            inter.append(MesureVect.from_raw((0,0,t1_th,x1,y1,z1)))
            # print(f"valeur gardée : {(0,0,t1_th,v)}")
            j += 1        
    inter.sort(key=lambda e: e.dateCreation)
    return inter

def interpolation_simple(mvt_exp, mvt_th):
    inter = []
    j = 0
    for i in range(0,len(mvt_exp)):
        t1_th = mvt_th[j].dateCreation
        t1 = mvt_exp[i].dateCreation
        v1 = mvt_exp[i].valeur
        # print(t1)
        # print(t1_th)
        if t1_th == t1:
            inter.append(MesureSimple.from_raw((0,0,t1,v1)))
            # print(f"valeur gardée : {(0,0,t1,v1)}")
            j += 1
        else:
            while t1_th < t1:
                t1_th = mvt_th[j].dateCreation
                v2 = mvt_exp[i-1].valeur
                t = t1_th
                v = (v1 + v2)/2
                inter.append(MesureSimple.from_raw((0,0,t,v)))
                j += 1
                t1_th = mvt_th[j].dateCreation
                # print(f"valeur ajoutée : {(0,0,t,v)}")
            inter.append(MesureSimple.from_raw((0,0,t1_th,v1)))
            # print(f"valeur gardée : {(0,0,t1_th,v)}")
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

def comparaison_direct(nom, dico_total, dico_exp):  
    data = ['pression', 'flexion', 'positions']
    dico_th = dico_total[nom]
    reponse = f'Le geste {nom} a été effectué avec :'
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
            if type == 'positions':
                mvt_exp_inter = interpolation_vect(mvt_exp, mvt_th_compare)
                mvt_exp = mvt_exp_inter
                if mvt_exp != 0 :  
                    for i in range(len(mvt_exp)):
                        x1 = mvt_th_compare[i].X
                        y1 = mvt_th_compare[i].Y
                        z1 = mvt_th_compare[i].Z    
                        x2 = mvt_exp[i].X
                        y2 = mvt_exp[i].Y
                        z2 = mvt_exp[i].Z
                        err_x = 100*abs(x1-x2)/x1
                        err_y = 100*abs(y1-y2)/y1
                        err_z = 100*abs(z1-z2)/z1
                        moy = (err_x + err_y + err_z)/3
                        res.append(moy)  
                    err_f = np.mean(res)
                    if err_f < err_i:
                        err_i = err_f
                    else:
                        text = "trop d'erreurs."
                        reponse += text
                        return reponse
                else:
                    text = "Aucun mouvmement enregistré, recommencer."
                    reponse += text
                    return reponse
                resultat = 100-err_i
                resultat = round(resultat, 2)
                text = f' {resultat}% de réussite en {type}'  
            else:
                mvt_exp_inter = interpolation_simple(mvt_exp, mvt_th_compare)
                mvt_exp = mvt_exp_inter
                if mvt_exp_inter != 0 :   
                    for i in range(len(mvt_exp)):
                        v1 = mvt_th_compare[i].valeur    
                        v2 = mvt_exp[i].valeur
                        err = 100*abs(v1-v2)
                        res.append(err)   
                    err_f = np.mean(res) 
                    if err_f < err_i:
                        err_i = err_f
                    else:
                        text = "trop d'erreurs"
                        return reponse
                else:
                    text = "Aucun mouvement enregistré, recommencer."
                    reponse += text
                    return reponse
                resultat = 100-err_i
                resultat = round(resultat, 2)
                text = f' {resultat}% de réussite en {type},'
        reponse += text
    return reponse +'.'

def comparaison_total(nom, dico_total, dico_exp):
    data = ['pression', 'flexion', 'positions']
    dico_th = dico_total[nom]
    reponse = f'Le geste {nom} a été effectué avec :'
    for type in data:
        mvt_exp = dico_exp[type]
        err_i = 100
        res = []
        mvt_exp_inter = []
        mvt_th = dico_th[type]
        duree_th = mvt_th[-1].dateCreation - mvt_th[0].dateCreation
        duree_exp = mvt_exp[-1].dateCreation - mvt_exp[0].dateCreation
        r = duree_exp/duree_th
        for row in mvt_exp:
            t = round(row.dateCreation/r)
            row.dateCreation = t               
        if type == 'positions':
            mvt_exp_inter = interpolation_vect(mvt_exp, mvt_th)
            mvt_exp = mvt_exp_inter
            if mvt_exp != 0 :  
                for i in range(len(mvt_exp)):
                    x1 = mvt_th[i].X
                    y1 = mvt_th[i].Y
                    z1 = mvt_th[i].Z    
                    x2 = mvt_exp[i].X
                    y2 = mvt_exp[i].Y
                    z2 = mvt_exp[i].Z
                    err_x = 100*abs(x1-x2)/x1
                    err_y = 100*abs(y1-y2)/y1
                    err_z = 100*abs(z1-z2)/z1
                    moy = (err_x + err_y + err_z)/3
                    res.append(moy)  
                err_f = np.mean(res)
                if err_f < err_i:
                    err_i = err_f
                else:
                    text = "trop d'erreurs."
                    reponse += text
                    return reponse
            resultat = 100-err_i
            resultat = round(resultat, 2)
            text = f' {resultat}% de réussite en {type}'  
        else:
            mvt_exp_inter = interpolation_simple(mvt_exp, mvt_th)
            mvt_exp = mvt_exp_inter
            if mvt_exp_inter != 0 :   
                for i in range(len(mvt_exp)):
                    v1 = mvt_th[i].valeur    
                    v2 = mvt_exp[i].valeur
                    err = 100*abs(v1-v2)
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
            text = f' {resultat}% de réussite en {type},'
        reponse += text
    return reponse +'.'


if __name__ == "__main__":
    mvt_exp = {'pression': MesureSimple.from_raw_list([(0,0,10,0),(0,0,13,0),(0,0,15,0)]),
               'flexion': MesureSimple.from_raw_list([(0,0,10,4),(0,0,13,5),(0,0,15,5)]), 
               'positions': MesureVect.from_raw_list([(0,0,10,9,8,4),(0,0,13,3,2,3),(0,0,15,10,8,1)])}

    mvt_exp2 = {'pression' : MesureSimple.from_raw_list([(0, 0, 0, 0),(0, 0, 1, 0), (0, 0, 2, 0), (0, 0, 3, 0), (0, 0, 4, 0),
                                        (0, 0, 5, 1), (0, 0, 6, 1), (0, 0, 7, 0), (0, 0, 8, 1), (0, 0, 9, 0), (0, 0, 10, 0), 
                                        (0, 0, 11, 0), (0, 0, 12, 1), (0, 0, 13, 0), (0, 0, 14, 0), (0, 0, 15, 0), (0, 0, 16, 0)]),
                    'flexion': MesureSimple.from_raw_list([(0, 0, 0, 0),(0, 0, 1, 4), (0, 0, 2, 2), (0, 0, 3, 4), (0, 0, 4, 2), (0, 0, 5, 3), 
                                        (0, 0, 6, 2), (0, 0, 7, 3), (0, 0, 8, 4), (0, 0, 9, 3), (0, 0, 10, 4), (0, 0, 11, 4), 
                                        (0, 0, 12, 5), (0, 0, 13, 5), (0, 0, 14, 3), (0, 0, 15, 5), (0, 0, 16, 3)]),
                    'positions': MesureVect.from_raw_list([(0, 0, 0, 3, 9, 9), (0, 0, 1, 3, 9, 9), (0, 0, 2, 4, 6, 8), 
                                        (0, 0, 3, 10, 1, 4), (0, 0, 4, 5, 5, 7), (0, 0, 5, 7, 6, 10), (0, 0, 6, 8, 2, 5), 
                                        (0, 0, 7, 6, 4, 4), (0, 0, 8, 2, 3, 2), (0, 0, 9, 10, 2, 9), (0, 0, 10, 9, 8, 4), 
                                        (0, 0, 11, 2, 9, 1), (0, 0, 12, 10, 4, 4), (0, 0, 13, 3, 2, 3), (0, 0, 14, 9, 1, 5), 
                                        (0, 0, 15, 10, 8, 1),(0, 0, 16, 4, 8, 1)])}
    
    data_th = {"aurevoir":{},
             "coucou":{'pression' : MesureSimple.from_raw_list([(0, 0, 0, 0),(0, 0, 1, 0), (0, 0, 2, 0), (0, 0, 3, 0), (0, 0, 4, 0),
                                        (0, 0, 5, 1), (0, 0, 6, 1), (0, 0, 7, 0), (0, 0, 8, 1), (0, 0, 9, 0), (0, 0, 10, 0), 
                                        (0, 0, 11, 0), (0, 0, 12, 1), (0, 0, 13, 0), (0, 0, 14, 0), (0, 0, 15, 0), (0, 0, 16, 0)]),
                    'flexion': MesureSimple.from_raw_list([(0, 0, 0, 0),(0, 0, 1, 4), (0, 0, 2, 2), (0, 0, 3, 4), (0, 0, 4, 2), (0, 0, 5, 3), 
                                        (0, 0, 6, 2), (0, 0, 7, 3), (0, 0, 8, 4), (0, 0, 9, 3), (0, 0, 10, 4), (0, 0, 11, 4), 
                                        (0, 0, 12, 5), (0, 0, 13, 5), (0, 0, 14, 3), (0, 0, 15, 5), (0, 0, 16, 3)]),
                    'positions': MesureVect.from_raw_list([(0, 0, 0, 3, 9, 9), (0, 0, 1, 3, 9, 9), (0, 0, 2, 4, 6, 8), 
                                        (0, 0, 3, 10, 1, 4), (0, 0, 4, 5, 5, 7), (0, 0, 5, 7, 6, 10), (0, 0, 6, 8, 2, 5), 
                                        (0, 0, 7, 6, 4, 4), (0, 0, 8, 2, 3, 2), (0, 0, 9, 10, 2, 9), (0, 0, 10, 9, 8, 4), 
                                        (0, 0, 11, 2, 9, 1), (0, 0, 12, 10, 4, 4), (0, 0, 13, 3, 2, 3), (0, 0, 14, 9, 1, 5), 
                                        (0, 0, 15, 10, 8, 1),(0, 0, 16, 4, 8, 1)])}}
    
    # test :
    texte = comparaison_direct("coucou",data_th, mvt_exp)   
    print(texte)
    texte2 = comparaison_total("coucou",data_th, mvt_exp2)   
    print(texte2)
    
