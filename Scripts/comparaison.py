# -*- coding: utf-8 -*-
"""
Created on Tue May 14 08:53:00 2024

@author: giaho
"""
from dataclass import MesureVect
import numpy as np
from random import randint


def interpolation(mvt_exp, mvt_th):
    inter = []
    j = 0
    for i in range(0,len(mvt_exp)):
        t1_th = mvt_th[j].dateCreation
        t1 = mvt_exp[i].dateCreation
        x1 = mvt_exp[i].X
        y1 = mvt_exp[i].Y
        z1 = mvt_exp[i].Z
        print(t1)
        print(t1_th)
        if t1_th == t1:
            inter.append(MesureVect.from_raw((0,0,t1,x1,y1,z1)))
            print(f"valeur gardée : {(0,0,t1,x1,y1,z1)}")
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
                print(f"valeur ajoutée : {(0,0,t,x,y,z)}")
            
    inter.sort(key=lambda e: e.dateCreation)
    return inter

def comparaison_direct(nom, data_th, mvt_exp):  
    err_i = 100
    # geste = ''  
    # for nom in data_th:
    res = []
    mvt_exp_inter = []
    # geste = nom 
    ti = mvt_exp[0].dateCreation
    tf = mvt_exp[-1].dateCreation
    mvt_th = data_th[nom] 
    mvt_th_compare = []  
    i = 0
    if ti != 0:
        while mvt_th[i].dateCreation < ti :
            i += 1
    while ti <= mvt_th[i].dateCreation <= tf:
        mvt_th_compare.append(mvt_th[i])
        i += 1
    mvt_exp_inter = interpolation(mvt_exp, mvt_th_compare)            
    if mvt_exp_inter != 0 :    
        for i in range(len(mvt_exp_inter)-1):
            x1 = mvt_th[i].X
            y1 = mvt_th[i].Y
            z1 = mvt_th[i].Z    
            x2 = mvt_exp_inter[i].X
            y2 = mvt_exp_inter[i].Y
            z2 = mvt_exp_inter[i].Z
            err_x = round((100*abs(x1-x2)/x1),2)
            err_y = round((100*abs(y1-y2)/y1),2)
            err_z = round((100*abs(z1-z2)/z1),2)
            moy = (err_x + err_y + err_z)/3
            res.append(moy)   
        err_f = np.mean(res) 
        if err_f < err_i:
            err_i = err_f
    else:
        text = "Aucun mouvement enregistré, recommencer."
    err_i = round(err_i,2)
    if err_i >50:
        text = f"Mouvement {nom} mal fait (plus de 50% d'erreurs), recommencer."  
    text = f'Le geste {nom} a été effectué avec {100-err_i}% de réussite.'
    return text

def comparaison_total(nom, data_th, mvt_exp):
    res = []
    err_i = 100
    th = data_th[nom]
    duree_th = th[-1].dateCreation - th[0].dateCreation
    duree_exp = mvt_exp[-1].dateCreation - mvt_exp[0].dateCreation
    r = duree_exp/duree_th
    for row in mvt_exp:
        t = round(row.dateCreation/r)
        row.dateCreation = t               
    exp = interpolation(mvt_exp,th)
    if exp != 0 :    
        for i in range(len(exp)-1):
            x1 = th[i].X
            y1 = th[i].Y
            z1 = th[i].Z
            
            x2 = exp[i].X
            y2 = exp[i].Y
            z2 = exp[i].Z
        
            err_x = round((100*abs(x1-x2)/x1),2)
            err_y = round((100*abs(y1-y2)/y1),2)
            err_z = round((100*abs(z1-z2)/z1),2)
            moy = (err_x + err_y + err_z)/3
            res.append(moy)   

        err_f = np.mean(res)
                
        if err_f < err_i:
            err_i = err_f
    else:
        text = "Aucun mouvement enregistré, recommencer."
    
    err_i = round(err_i,2)
    if err_i >50:
        text = f"Mouvement {nom} mal fait (plus de 50% d'erreurs), recommencer."  
    text = f'Le geste {nom} a été effectué avec {100-err_i}% de réussite.'
    return text




# data = []
# for t in range(1,16):
#     x = randint(1,10)
#     y = randint(1,10)
#     z = randint(1,10)
#     data.append((0,0,t,x,y,z))

if __name__ == "__main__":
    mvt_exp = MesureVect.from_raw_list([(0,0,10,2,3,1),(0,0,13,5,6,2),(0,0,15,8,9,3)])

    mvt_exp2 = MesureVect.from_raw_list([(0, 0, 0, 3, 9, 9), (0, 0, 6, 10, 1, 4), (0, 0, 8, 5, 5, 7), 
                                        (0, 0, 10, 7, 6, 10), (0, 0, 12, 8, 2, 5), (0, 0, 16, 2, 3, 2), 
                                        (0, 0, 18, 10, 2, 9), (0, 0, 20, 9, 8, 4), (0, 0, 22, 2, 9, 1), 
                                        (0, 0, 26, 3, 2, 3), (0, 0, 30, 10, 8, 1), (0, 0, 32, 4, 8, 1)])
    
    # ([(0, 0, 0, 3, 9, 9), (0, 0, 3, 10, 1, 4), (0, 0, 4, 5, 5, 7), 
    # (0, 0, 5, 7, 6, 10), (0, 0, 6, 8, 2, 5), (0, 0, 8, 2, 3, 2), 
    # (0, 0, 9, 10, 2, 9), (0, 0, 10, 9, 8, 4), (0, 0, 11, 2, 9, 1), 
    # (0, 0, 13, 3, 2, 3), (0, 0, 15, 10, 8, 1), (0, 0, 16, 4, 8, 1)])
    
    data_th = {"aurevoir":MesureVect.from_raw_list([(0,0,0,9,8,1),(0,0,1,6,5,1.5),(0,0,2,3,2,2),(0,0,3,1,1,2.6),(0,0,4,2,3,3)]),
           "coucou":MesureVect.from_raw_list([(0, 0, 0, 3, 9, 9), (0, 0, 1, 3, 9, 9), (0, 0, 2, 4, 6, 8), (0, 0, 3, 10, 1, 4), 
                                              (0, 0, 4, 5, 5, 7), (0, 0, 5, 7, 6, 10), (0, 0, 6, 8, 2, 5), (0, 0, 7, 6, 4, 4), 
                                              (0, 0, 8, 2, 3, 2), (0, 0, 9, 10, 2, 9), (0, 0, 10, 9, 8, 4), (0, 0, 11, 2, 9, 1), 
                                              (0, 0, 12, 10, 4, 4), (0, 0, 13, 3, 2, 3), (0, 0, 14, 9, 1, 5), (0, 0, 15, 10, 8, 1), 
                                              (0, 0, 16, 4, 8, 1)])}
    
    # print(data)
    texte = comparaison_direct("coucou",data_th, mvt_exp)   
    print(texte)
    texte2 = comparaison_total("coucou",data_th, mvt_exp2)   
    print(texte2)
    
