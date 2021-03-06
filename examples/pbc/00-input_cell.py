#!/usr/bin/env python

import numpy
import pyscf.lib
from pyscf.pbc import gto

#
# Simliar to the initialization of "Mole" object, here we need create a "Cell"
# object for periodic boundary systems.
#
cell = gto.Cell()
cell.atom = '''C     0.      0.      0.    
              C     0.8917  0.8917  0.8917
              C     1.7834  1.7834  0.    
              C     2.6751  2.6751  0.8917
              C     1.7834  0.      1.7834
              C     2.6751  0.8917  2.6751
              C     0.      1.7834  1.7834
              C     0.8917  2.6751  2.6751'''
cell.basis = 'gth-szv'
cell.pseudo = 'gth-pade'
#
# Note two extra attributes ".h", ".gs" for in the "cell" initialization.
# .h is a matrix for lattice vectors.  Note each column of .h denotes a direction
#
cell.h = numpy.eye(3)*3.5668
cell.gs = [10]*3  # 10 grids on postive x direction, => 21^3 grids in total
cell.build()

#
# pbc.gto module provided a shortcut initialization function "gto.M", like the
# one of finite size problem
#
cell = gto.M(
    atom = '''C     0.      0.      0.    
              C     0.8917  0.8917  0.8917
              C     1.7834  1.7834  0.    
              C     2.6751  2.6751  0.8917
              C     1.7834  0.      1.7834
              C     2.6751  0.8917  2.6751
              C     0.      1.7834  1.7834
              C     0.8917  2.6751  2.6751''',
    basis = 'gth-szv',
    pseudo = 'gth-pade',
    h = numpy.eye(3)*3.5668,
    gs = [10]*3)

