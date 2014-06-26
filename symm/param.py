#
# File: param.py
# Author: Qiming Sun <osirpt.sun@gmail.com>
#

# D2h   C2h   C2v   D2   Cs   Ci   C2   C1
# E     E     E     E    E    E    E    E
# C2x               C2x
# C2y               C2y
# C2z   C2    C2    C2z            C2
# i     i                     i
# sx          sx
# sy          sy
# sz    sh                sh

POINTGROUP = ('D2h', 'C2h', 'C2v', 'D2' , 'Cs' , 'Ci' , 'C2' , 'C1' ,)

OPERATOR_TABLE = {
    'D2h': ('E', 'C2x', 'C2y', 'C2z', 'i', 'sx' , 'sy' , 'sz' ),
    'C2h': ('E',               'C2z', 'i',               'sz' ),
    'C2v': ('E',               'C2z',      'sx' , 'sy' ,      ),
    'D2' : ('E', 'C2x', 'C2y', 'C2z',                         ),
    'Cs' : ('E',                                         'sz' ),
    'Ci' : ('E',                      'i',                    ),
    'C2' : ('E',               'C2z',                         ),
    'C1' : ('E',                                              ),
}

#
IRREP_ID_TABLE = {
                        # bin for XOR
    'D2h': {'Ag' : 0,   # 000
            'B1g': 1,   # 001
            'B2g': 2,   # 010
            'B3g': 3,   # 011
            'Au' : 4,   # 100
            'B1u': 5,   # 101
            'B2u': 6,   # 110
            'B3u': 7,}, # 111
    'C2h': {'Ag': 0,    # 00
            'Bg': 1,    # 01
            'Au': 2,    # 10
            'Bu': 3,},  # 11
    'C2v': {'A1': 0,    # 00
            'A2': 1,    # 01
            'B1': 2,    # 10
            'B2': 3,},  # 11
    'D2' : {'A' : 0,    # 00
            'B1': 1,    # 01
            'B2': 2,    # 10
            'B3': 3,},  # 11
    'Cs' : {'A1': 0,    # 0
            'A2': 1,},  # 1
    'Ci' : {'Ag': 0,    # 0
            'Au': 1,},  # 1
    'C2' : {'A': 0,     # 0
            'B': 1,},   # 1
    'C1' : {'A': 1,},   # 0
}

#                   E,C2x,C2y,C2z,i, sx,sy,sz
CHARACTER_TABLE = {                              # XOR
    'D2h': (('Ag' , 1, 1,  1,  1,  1, 1, 1, 1),  # 000
            ('B1g', 1,-1, -1,  1,  1,-1,-1, 1),  # 001
            ('B2g', 1,-1,  1, -1,  1,-1, 1,-1),  # 010
            ('B3g', 1, 1, -1, -1,  1, 1,-1,-1),  # 011
            ('Au' , 1, 1,  1,  1, -1,-1,-1,-1),  # 100
            ('B1u', 1,-1, -1,  1, -1, 1, 1,-1),  # 101
            ('B2u', 1,-1,  1, -1, -1, 1,-1, 1),  # 110
            ('B3u', 1, 1, -1, -1, -1,-1, 1, 1)), # 111
#                  E,C2,i, sh                    # XOR
    'C2h': (('Ag', 1, 1, 1, 1),                  # 00
            ('Bg', 1,-1, 1,-1),                  # 01
            ('Au', 1, 1,-1,-1),                  # 10
            ('Bu', 1,-1,-1, 1)),                 # 11
#                  E,C2,sx,sy                    # XOR
    'C2v': (('A1', 1, 1, 1, 1),                  # 00
            ('A2', 1, 1,-1,-1),                  # 01
            ('B1', 1,-1,-1, 1),                  # 10
            ('B2', 1,-1, 1,-1)),                 # 11
#                  E,C2x,C2y,C2z                 # XOR
    'D2' : (('A' , 1, 1,  1,  1),                # 00
            ('B1', 1,-1, -1,  1),                # 01
            ('B2', 1,-1,  1, -1),                # 10
            ('B3', 1, 1, -1, -1)),               # 11
#                  E, sh                         # XOR
    'Cs' : (('A1', 1, 1,),                       # 0
            ('A2', 1,-1,)),                      # 1
#                  E, i                          # XOR
    'Ci' : (('Ag', 1, 1,),                       # 0
            ('Au', 1,-1,)),                      # 1
#                 E, C2                          # XOR
    'C2' : (('A', 1, 1,),                        # 0
            ('B', 1,-1,)),                       # 1
#                 E                              # XOR
    'C1' : (('A', 1),),                          # 0
}

#     D2h   C2h   C2v   D2   Cs   Ci   C2   C1
SYMM_DECENT_Z = (
    ('Ag' , 'Ag', 'A1', 'A' , 'A1', 'Ag', 'A', 'A'),
    ('B1g', 'Ag', 'A2', 'B1', 'A1', 'Ag', 'A', 'A'),
    ('B2g', 'Bg', 'B1', 'B2', 'A2', 'Ag', 'B', 'A'),
    ('B3g', 'Bg', 'B2', 'B3', 'A2', 'Ag', 'B', 'A'),
    ('Au' , 'Au', 'A2', 'A' , 'A1', 'Au', 'A', 'A'),
    ('B1u', 'Au', 'A1', 'B1', 'A1', 'Au', 'A', 'A'),
    ('B2u', 'Bu', 'B2', 'B2', 'A2', 'Au', 'B', 'A'),
    ('B3u', 'Bu', 'B1', 'B3', 'A2', 'Au', 'B', 'A'),
)
SYMM_DECENT_X = (
    ('Ag' , 'Ag', 'A1', 'A' , 'A1', 'Ag', 'A', 'A'),
    ('B1g', 'Bg', 'B2', 'B1', 'A2', 'Ag', 'B', 'A'),
    ('B2g', 'Bg', 'B1', 'B2', 'A2', 'Ag', 'B', 'A'),
    ('B3g', 'Ag', 'A2', 'B3', 'A1', 'Ag', 'A', 'A'),
    ('Au' , 'Au', 'A2', 'A' , 'A2', 'Au', 'A', 'A'),
    ('B1u', 'Bu', 'B1', 'B1', 'A1', 'Au', 'B', 'A'),
    ('B2u', 'Bu', 'B2', 'B2', 'A1', 'Au', 'B', 'A'),
    ('B3u', 'Au', 'A1', 'B3', 'A2', 'Au', 'A', 'A'),
)
SYMM_DECENT_Y = (
    ('Ag' , 'Ag', 'A1', 'A' , 'A1', 'Ag', 'A', 'A'),
    ('B1g', 'Bg', 'B2', 'B1', 'A2', 'Ag', 'B', 'A'),
    ('B2g', 'Ag', 'A2', 'B2', 'A1', 'Ag', 'A', 'A'),
    ('B3g', 'Bg', 'B1', 'B3', 'A2', 'Ag', 'B', 'A'),
    ('Au' , 'Au', 'A2', 'A' , 'A2', 'Au', 'A', 'A'),
    ('B1u', 'Bu', 'B1', 'B1', 'A1', 'Au', 'B', 'A'),
    ('B2u', 'Au', 'A1', 'B2', 'A2', 'Au', 'A', 'A'),
    ('B3u', 'Bu', 'B2', 'B3', 'A1', 'Au', 'B', 'A'),
)


SPHERIC_GTO_PARITY_ODD = (
# s
    ((0, 0, 0),),
# py, pz, px
    ((0, 1, 0),(0, 0, 1),(1, 0, 0)),
# dxy, dyz, dz2, dxz, dx2y2
    ((1, 1, 0),(0, 1, 1),(0, 0, 0),(1, 0, 1),(0, 0, 0),),
# fyx2, fxyz, fyz2, fz3, fxz2, fzx2, fx3
    ((0, 1, 0),(1, 1, 1),(0, 1, 0),(0, 0, 1),(1, 0, 0),
     (0, 0, 1),(1, 0, 0),),
# g
    ((1, 1, 0),(0, 1, 1),(1, 1, 0),(0, 1, 1),(0, 0, 0),
     (1, 0, 1),(0, 0, 0),(1, 0, 1),(0, 0, 0),),
# h
    ((0, 1, 0),(1, 1, 1),(0, 1, 0),(1, 1, 1),(0, 1, 0),
     (0, 0, 1),(1, 0, 0),(0, 0, 1),(1, 0, 0),(0, 0, 1),
     (1, 0, 0),),
)