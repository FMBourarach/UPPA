#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 2 09:47 2023

@author: fmbourarach
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import sys


def progress(count, total, status="Thermal Simulation "):
    """
    [New function]
    Prints a progress bar in Anaconda Prompt

    REFERENCE:
    ----------
    http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113
    """
    bar_len = 50
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)

    sys.stdout.write("[%s] %s%s ...%s\r" % (bar, percents, "%", status))
    sys.stdout.flush()


# ========================================
# Déclaration des paramètres
# ========================================

mMax = 20       # [-] nombre de pas d'espace

R = 1         # [m] épaisseur du mur
D = 60*60        # [s] durée de la simulation

dt = 0.1        # [s] pas de temps de simulation
dtLog = 72       # [s] pas de temps de sauvegardeè2

rho = 2*240       # [kg/m3] masse volumique
C = 800 # [kg/m3] capacité calorifique
k = 35 # [W/(m.K)] conductivité thermique

### Choisir les conditions aux limites

TG =  10     # Temperature imposée côté gauche °C
TD =  100     # Temperature imposée côté droit °C

T_air_droit = 100 # °C
h_droit = 10000 # W.m-2.K-1
T_air_gauche = 25 # °C
h_gauche = 20 # W.m-2.K-1

T0 = 35         # [°C] température initiale



# ========================================
# préparation des géométries
# ========================================

dx = R/mMax # distance elementaire
S = 1 # Surface m²
V = S * dx

# ========================================
# Routine d'export
# ========================================
data = np.zeros((0,3)) # variable pour le tracé de l'évolution temporelle
def export():
    global data
    x = [ dx for m in range(mMax)]
    plt.plot(x,T, label=f"{time:10.2f}s")
    plt.legend()
    data = np.append(data, [[time, T[0], T[mMax-1]]], axis=0)

# ========================================
# Résolution
# ========================================

T = np.zeros((int(D/dt),mMax))
T[0::] = T0       # Condition initiale
EVOL = np.zeros(mMax)

for time in range(1,int(D/dt)): # temps physique [s]
    progress(time, int(D/dt)-1, status="Mur 1D permanant")
    for m in range(mMax):
        # Calcul du flux GAUCHE
        if m==0:
            flux_gauche = 2*k*S/dx * (      TG      - T[time-1,m])
        else:
            flux_gauche =   k*S/dx * (T[time-1,m-1] - T[time-1,m])

        # Calcul du flux DROIT
        if m==mMax-1:
            # flux_droit = 2*k*S/dx * (     TD       - T[time-1,m])
            flux_droit = S/(dx/(k*2) + 1/h_droit) * (     T_air_droit       - T[time-1,m])
        else:
            flux_droit =   k*S/dx * (T[time-1,m+1] - T[time-1,m])

        # calculer le bilan
        EVOL[m] = (flux_gauche + flux_droit)/(rho*C*V/dt)
    
    # préparer l'itération suivante
    T[time,:] = T[time-1,:] + EVOL[:]
    time = time + dt


# ========================================
# Graphiques
# ========================================

# ----------- Statique -------------
plt.ylim((min(TG,TD)-1, max(TG,TD)+1))
plt.plot(T[0::250,:].T)
plt.axhline(y=TG, color='r', linestyle='--', label="TG")
plt.axhline(y=TD, color='r', linestyle='--', label="TD")
plt.show()

# ------------ Animation ------------
T_sliced = T[0::50,::] #

fig = plt.figure()
ax = plt.axes(xlim=(0, mMax), ylim=(min(TG,TD)-1, max(TG,TD)+1))
line, = ax.plot([], [])

def init():
    line.set_data([], [])
    return line,

def animate(i):
    line.set_data(range(0,len(T_sliced[i,:])), T_sliced[i,:])
    return line,

anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=int(D/dt)//100, interval=dt/1000, blit=True)

print("stop")