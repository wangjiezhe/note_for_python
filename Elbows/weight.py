#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
from functools import partial
import pandas as pd


def pipe_weight_pm(rho, D, S):
    return rho * np.pi * S * 10**(-3) * (D-S) * 10**(-3)


def pipe_density(w, D, S):
    return w / (np.pi * S * 10**(-3) * (D-S) * 10**(-3))


rho_carbon_steel = 7.85 * 10**3

carbon_steel_pipe_weight_pm = partial(pipe_weight_pm, rho=rho_carbon_steel)


def elbow_90e_weight(D, S, R, rho=rho_carbon_steel):
    return pipe_weight_pm(rho, D, S) * np.pi / 2 * R * 10**(-3)


def elbow_45e_weight(D, S, R, rho=rho_carbon_steel):
    return elbow_90e_weight(D, S, R, rho) / 2


def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(src_dir)
    DNtoA = pd.read_csv('DNtoA.csv')
    DNtoOD = pd.read_csv('DNtoOD.csv')
    DNandS = pd.read_csv('DNandS.csv')
    DNtoA = DNtoA.set_index('DN')
    DNtoOD = DNtoOD.set_index('DN')
    weights = [elbow_90e_weight(DNtoOD.loc[col['DN'].astype(int)]['OD'],
                                col['S'],
                                DNtoA.loc[col['DN'].astype(int)]['A'])
               for _, col in DNandS.iterrows()]
    for w in weights:
        print(w)


if __name__ == '__main__':
    main()
