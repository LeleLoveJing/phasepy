

from __future__ import division, print_function, absolute_import
import numpy as np 
from ..constants import R

#ajuste parametros alpha de EOS 
def psat(T, cubic, P0 = None):
    """
    Computes saturation pressure with cubic eos
    
    Parameters
    ----------
    T : float,
        temperatura a la que se evalua la presion, en kelvin
    cubic : object
          objeto creado a partir de puro y ecuacion de estado
    Returns
    -------   
    P : float
       saturation pressure
    """
    a = cubic.a_eos(T)
    b = cubic.b
    c1 = cubic.c1
    c2 = cubic.c2
    emin = cubic.emin
    e=a/(b*R*T)
    
    if T == cubic.Tc:
        return cubic.Pc
    if P0 == None:
        if e> emin: #metodo iniciacion presion cero
            U = (e-c1-c2-np.sqrt((e-c1-c2)**2-4*(c1*c2+e)))/2;
            if c1 == 0 and c2 == 0:
                S = -1-np.log(U-1)-e/U
            else:
                S = -1-np.log(U-1)-e*np.log((U+c1)/(U+c2))/(c1-c2);
            P=np.exp(S)*R*T/b; #bar
        else: #metodo iniciacion presion media
            a1=-R*T
            a2=-2*b*R*T*(c1+c2)+2*a
            a3=-R*T*b**2*(c1**2+4*c1*c2+c2**2)+a*b*(c1+c2-4)
            a4=-R*T*2*b**3*c1*c2*(c1+c2)+2*a*b**2*(1-c1-c2)
            a5=-R*T*b**4*c1*c2+a*b**3*(c1+c2)
            V=np.roots([a1,a2,a3,a4,a5])
            V=V[np.isreal(V)]
            V=V[V>b]
            P = cubic(T,V)
            P[P<0] = 0.
            P = P.mean()
    else:
        P =  P0 

    itmax=20
    for k in range(itmax):
        A=a*P/(R*T)**2
        B=b*P/(R*T)
        Z = cubic._Zroot(A,B)
        Zl = min(Z)
        Zv = max(Z)
        fugL = cubic._logfug_aux(Zl, A, B)
        fugV = cubic._logfug_aux(Zv, A, B)
        FO=fugV-fugL
        dFO=(Zv-Zl)/P
        dP=FO/dFO
        P -= dP
        if abs(dP)<1e-8: break
    return P