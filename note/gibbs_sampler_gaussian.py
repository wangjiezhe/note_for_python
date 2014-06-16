#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''利用Gibbs抽样产生二元正态分布的随机数'''


import random
import numpy


class Gibbsforgauss(object):
    def __init__(self, N, off, rho, mu1, mu2, sigma1, sigma2):
        '''initialize constants and parameters'''
        self.N = N  # length of chain
        self.off = off  # discarded length
        self.X = numpy.zeros((N, 2)).tolist()
        self.rho = rho
        self.mu1 = mu1
        self.mu2 = mu2
        self.sigma1 = sigma1
        self.sigma2 = sigma2

    def generate(self):
        '''generate the chain'''
        s1 = numpy.sqrt(1-self.rho**2)*self.sigma1
        s2 = numpy.sqrt(1-self.rho**2)*self.sigma2
        self.X[0] = [self.mu1, self.mu2]
        for i in range(0, self.N-1):
            X2 = self.X[i][1]
            m1 = self.mu1+self.rho*(X2-self.mu2)*self.sigma1/self.sigma2
            self.X[i+1][0] = random.gauss(m1, s1)
            X1 = self.X[i][0]
            m2 = self.mu2+self.rho*(X1-self.mu1)*self.sigma2/self.sigma1
            self.X[i+1][1] = random.gauss(m2, s2)
        Y = self.X[self.off:self.N]
        return Y


def main():
    N = 1000
    off = 900
    rho = -0.5
    mu1 = 0
    mu2 = 1
    sigma1 = 1
    sigma2 = 0.5
    X = Gibbsforgauss(N, off, rho, mu1, mu2, sigma1, sigma2)
    Y = X.generate()
    k = 1
    for ii in Y:
        print "%3d: (% .10f, % .10f)" % (k, ii[0], ii[1])
        k += 1


if __name__ == '__main__':
    main()
