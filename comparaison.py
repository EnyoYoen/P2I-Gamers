# -*- coding: utf-8 -*-
"""
Created on Tue May 14 08:53:00 2024

@author: giaho
"""
from Class import MesureVect 
import matplotlib.pyplot as plt
import numpy as np

mvt_exp = MesureVect.from_raw_list([(1,2,3,1), (4,5,6,2),(7,8,9,3)])
data_th = {"aurevoir":MesureVect.from_raw_list([(10,9,8,1),(7,6,5,1.5),(4,3,2,2),(1,1,1,2.6),(1,2,3,3)]),
           "coucou":MesureVect.from_raw_list([(1,2,3,1),(4,5,6,1.5),(7,8,9,2),(1,1,1,2.6),(1,2,3,3)])}


def interpolation(mvt, mvt_th):
    
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
            mvt.append(MesureVect.from_raw((x,y,z,t)))
        else:
            mvt.append(MesureVect.from_raw((x1,y1,z1,t1)))
    mvt.sort(key=lambda e: e.dateCreation)

    return mvt

def comparaison(data_th, mvt_exp):  
    err_i = 1000
    geste = ''
    
    for nom in data_th:
        res = []
        geste = nom 
        mvt_th = data_th[nom]
        mvt_th.sort(key=lambda e: e.dateCreation)
        
        mvt_exp_inter = interpolation(mvt_exp, mvt_th)
        print(mvt_exp)
        print(mvt_th)
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
                moy = (err_x+err_y+err_z)/3
                res.append(moy)   
            
            err_f = np.mean(res)
                        
            if err_f < err_i:
                err_i = err_f
                geste = nom 
            
            if err_i >50:
                print("faux mvt")
                
        else:
            print("mvt non enregistré")
    
    return geste, err_i
        
        
geste, err = comparaison(data_th, mvt_exp)   

print(geste, err)
    