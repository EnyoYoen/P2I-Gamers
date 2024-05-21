# -*- coding: utf-8 -*-
"""
Created on Tue May 14 08:53:00 2024

@author: giaho
"""
from dataclass import MesureVect
import numpy as np


# test :
# mvt_exp = MesureVect.from_raw_list([(0,0,1,2,3,1),(1,1,4,5,6,2),(2,2,7,8,9,3)])
# data_th = {"aurevoir":MesureVect.from_raw_list([(0,3,10,9,8,1),(0,4,7,6,5,1.5),(0,5,4,3,2,2),(0,6,1,1,1,2.6),(0,7,1,2,3,3)]),
#            "coucou":MesureVect.from_raw_list([(0,13,1,2,3,1),(0,12,4,5,6,1.5),(0,11,7,8,9,2),(0,10,1,1,1,2.6),(0,9,1,2,3,3),(0,8,0,0,0,4)])}

def interpolation(mvt, mvt_th):
    inter = []
    for i in mvt:
        inter.append(i)
    for i in range(len(mvt)-1):
        t1_th = mvt_th[i].dateCreation
        t1 = mvt[i].dateCreation
        x1 = mvt[i].X
        y1 = mvt[i].Y
        z1 = mvt[i].Z
        
        t2 = mvt[i+1].dateCreation
        x2 = mvt[i+1].X
        y2 = mvt[i+1].Y
        z2 = mvt[i+1].Z
                
        if t1 != t1_th:
            t = (t1+t2)/2
            x = (x1+x2)/2
            y = (y1+y2)/2
            z = (z1+z2)/2       
            inter.append(MesureVect.from_raw((0,0,x,y,z,t)))
            
    inter.sort(key=lambda e: e.dateCreation)
    return inter

def comparaison(data_th, mvt_exp):  
    err_i = 100
    geste = ''
    
    for nom in data_th:
        res = []
        mvt_exp_inter = []
        geste = nom 
        mvt_th = data_th[nom]    
        mvt_exp_inter = interpolation(mvt_exp, mvt_th)
               
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
                geste = nom    
        else:
            text = "Aucun mouvement enregistré, recommencer."
    
    err_i = round(err_i,2)
    if err_i >50:
        text = f"Mouvement {geste} mal fait (plus de 50% d'erreurs), recommencer."  
    text = f'Le geste {geste} a été effectué avec {100-err_i}% de réussite.'
    return text
        
        
# geste, err = comparaison(data_th, mvt_exp)   
# print(f'Le geste {geste} a été effectué avec {100-err}% de réussite.')