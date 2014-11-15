#!/usr/bin/env python
# $Id$
# -*- coding: utf-8
#
# FCI solver for arbitary number of alpha and beta electrons.  The hamiltonian
# requires spacial part of the integrals (RHF/ROHF MO integrals).  This solver
# can be used to compute doublet, triplet,...
#
# Other files in the directory
# direct_ms0   MS=0, same number of alpha and beta nelectrons
# direct_spin0 singlet
# direct_spin1 arbitary number of alpha and beta electrons, based on RHF/ROHF
#              MO integrals
# direct_uhf   arbitary number of alpha and beta electrons, based on UHF
#              MO integrals
#

import os
import ctypes
import numpy
import pyscf.lib
import pyscf.ao2mo
import davidson
import cistring
import direct_spin0
import rdm

_loaderpath = os.path.dirname(pyscf.lib.__file__)
libfci = numpy.ctypeslib.load_library('libmcscf', _loaderpath)

def contract_1e(f1e, fcivec, norb, nelec, link_index=None):
    neleca, nelecb = nelec
    if link_index is None:
        link_indexa = cistring.gen_linkstr_index_trilidx(range(norb), neleca)
        link_indexb = cistring.gen_linkstr_index_trilidx(range(norb), nelecb)
    else:
        link_indexa, link_indexb = link_index

    na, nlinka = link_indexa.shape[:2]
    nb, nlinkb = link_indexb.shape[:2]
    f1e_tril = pyscf.lib.pack_tril(f1e)
    ci1 = numpy.zeros((na,nb))
    libfci.FCIcontract_a_1e(f1e_tril.ctypes.data_as(ctypes.c_void_p),
                            fcivec.ctypes.data_as(ctypes.c_void_p),
                            ci1.ctypes.data_as(ctypes.c_void_p),
                            ctypes.c_int(norb),
                            ctypes.c_int(na), ctypes.c_int(nb),
                            ctypes.c_int(nlinka), ctypes.c_int(nlinkb),
                            link_indexa.ctypes.data_as(ctypes.c_void_p),
                            link_indexb.ctypes.data_as(ctypes.c_void_p))
    libfci.FCIcontract_b_1e(f1e_tril.ctypes.data_as(ctypes.c_void_p),
                            fcivec.ctypes.data_as(ctypes.c_void_p),
                            ci1.ctypes.data_as(ctypes.c_void_p),
                            ctypes.c_int(norb),
                            ctypes.c_int(na), ctypes.c_int(nb),
                            ctypes.c_int(nlinka), ctypes.c_int(nlinkb),
                            link_indexa.ctypes.data_as(ctypes.c_void_p),
                            link_indexb.ctypes.data_as(ctypes.c_void_p))
    return ci1

# the input fcivec should be symmetrized
def contract_2e(g2e, fcivec, norb, nelec, link_index=None, bufsize=1024):
    neleca, nelecb = nelec
    g2e = pyscf.ao2mo.restore(4, g2e, norb)
    if not g2e.flags.c_contiguous:
        g2e = g2e.copy()
    if link_index is None:
        link_indexa = cistring.gen_linkstr_index_trilidx(range(norb), neleca)
        link_indexb = cistring.gen_linkstr_index_trilidx(range(norb), nelecb)
    else:
        link_indexa, link_indexb = link_index

    na, nlinka = link_indexa.shape[:2]
    nb, nlinkb = link_indexb.shape[:2]
    fcivec = fcivec.reshape(na,nb)
    ci1 = numpy.empty_like(fcivec)

    libfci.FCIcontract_rhf2e_spin1(g2e.ctypes.data_as(ctypes.c_void_p),
                                   fcivec.ctypes.data_as(ctypes.c_void_p),
                                   ci1.ctypes.data_as(ctypes.c_void_p),
                                   ctypes.c_int(norb),
                                   ctypes.c_int(na), ctypes.c_int(nb),
                                   ctypes.c_int(nlinka), ctypes.c_int(nlinkb),
                                   link_indexa.ctypes.data_as(ctypes.c_void_p),
                                   link_indexb.ctypes.data_as(ctypes.c_void_p),
                                   ctypes.c_int(bufsize))
    return ci1

def make_hdiag(h1e, g2e, norb, nelec):
    neleca, nelecb = nelec
    g2e = pyscf.ao2mo.restore(1, g2e, norb)
    link_indexa = cistring.gen_linkstr_index(range(norb), neleca)
    link_indexb = cistring.gen_linkstr_index(range(norb), nelecb)
    na = link_indexa.shape[0]
    nb = link_indexb.shape[0]

    occslista = link_indexa[:,:neleca,0].copy('C')
    occslistb = link_indexb[:,:nelecb,0].copy('C')
    hdiag = numpy.empty(na*nb)
    jdiag = numpy.einsum('iijj->ij',g2e).copy('C')
    kdiag = numpy.einsum('ijji->ij',g2e).copy('C')
    libfci.FCImake_hdiag_uhf(hdiag.ctypes.data_as(ctypes.c_void_p),
                             h1e.ctypes.data_as(ctypes.c_void_p),
                             h1e.ctypes.data_as(ctypes.c_void_p),
                             jdiag.ctypes.data_as(ctypes.c_void_p),
                             jdiag.ctypes.data_as(ctypes.c_void_p),
                             jdiag.ctypes.data_as(ctypes.c_void_p),
                             kdiag.ctypes.data_as(ctypes.c_void_p),
                             kdiag.ctypes.data_as(ctypes.c_void_p),
                             ctypes.c_int(norb),
                             ctypes.c_int(na), ctypes.c_int(nb),
                             ctypes.c_int(neleca), ctypes.c_int(nelecb),
                             occslista.ctypes.data_as(ctypes.c_void_p),
                             occslistb.ctypes.data_as(ctypes.c_void_p))
    return numpy.array(hdiag)

def absorb_h1e(h1e, g2e, norb, nelec):
    return direct_spin0.absorb_h1e(h1e, g2e, norb, nelec[0]+nelec[1])

def pspace(h1e, g2e, norb, nelec, hdiag, np=400):
    neleca, nelecb = nelec
    g2e = pyscf.ao2mo.restore(1, g2e, norb)
    na = cistring.num_strings(norb, neleca)
    nb = cistring.num_strings(norb, nelecb)
    addr = numpy.argsort(hdiag)[:np]
    addra = addr / nb
    addrb = addr % nb
    stra = numpy.array([cistring.addr2str(norb,neleca,ia) for ia in addra],
                       dtype=numpy.long)
    strb = numpy.array([cistring.addr2str(norb,nelecb,ib) for ib in addrb],
                       dtype=numpy.long)
    np = len(addr)
    h0 = numpy.zeros((np,np))
    libfci.FCIpspace_h0tril(h0.ctypes.data_as(ctypes.c_void_p),
                            h1e.ctypes.data_as(ctypes.c_void_p),
                            g2e.ctypes.data_as(ctypes.c_void_p),
                            stra.ctypes.data_as(ctypes.c_void_p),
                            strb.ctypes.data_as(ctypes.c_void_p),
                            ctypes.c_int(norb), ctypes.c_int(np))

    for i in range(np):
        h0[i,i] = hdiag[addr[i]]
    h0 = pyscf.lib.hermi_triu(h0)
    return addr, h0

# be careful with single determinant initial guess. It may lead to the
# eigvalue of first davidson iter being equal to hdiag
def kernel(h1e, g2e, norb, nelec, ci0=None, eshift=.001):
    neleca, nelecb = nelec
    link_indexa = cistring.gen_linkstr_index_trilidx(range(norb), neleca)
    link_indexb = cistring.gen_linkstr_index_trilidx(range(norb), nelecb)
    na = link_indexa.shape[0]
    nb = link_indexb.shape[0]
    h2e = absorb_h1e(h1e, g2e, norb, nelec) * .5
    hdiag = make_hdiag(h1e, g2e, norb, nelec)

    addr, h0 = pspace(h1e, g2e, norb, nelec, hdiag)
    pw, pv = numpy.linalg.eigh(h0)
    if len(addr) == na*nb:
        ci0 = numpy.empty((na*nb))
        ci0[addr] = pv[:,0]
        return pw[0], ci0.reshape(na,nb)

    def precond(r, e0, x0, *args):
        #h0e0 = h0 - numpy.eye(len(addr))*(e0-eshift)
        h0e0inv = numpy.dot(pv/(pw-(e0-eshift)), pv.T)
        hdiaginv = 1/(hdiag - (e0-eshift))
        h0x0 = x0 * hdiaginv
        #h0x0[addr] = numpy.linalg.solve(h0e0, x0[addr])
        h0x0[addr] = numpy.dot(h0e0inv, x0[addr])
        h0r = r * hdiaginv
        #h0r[addr] = numpy.linalg.solve(h0e0, r[addr])
        h0r[addr] = numpy.dot(h0e0inv, r[addr])
        e1 = numpy.dot(x0, h0r) / numpy.dot(x0, h0x0)
        x1 = r - e1*x0
        #pspace_x1 = x1[addr].copy()
        x1 *= hdiaginv
# pspace (h0-e0)^{-1} cause diverging?
        #x1[addr] = numpy.linalg.solve(h0e0, pspace_x1)
        return x1

    h2e = pyscf.ao2mo.restore(1, h2e, norb)
    def hop(c):
        hc = contract_2e(h2e, c, norb, nelec, (link_indexa,link_indexb))
        return hc.ravel()

    if ci0 is None:
        ci0 = numpy.zeros(na*nb)
        ci0[0] = 1
    else:
        ci0 = ci0.ravel()

    e, c = davidson.dsyev(hop, ci0, precond, tol=1e-8, lindep=1e-8)
    return e, c.reshape(na,nb)

def energy(h1e, g2e, fcivec, norb, nelec, link_index=None):
    h2e = absorb_h1e(h1e, g2e, norb, nelec) * .5
    ci1 = contract_2e(h2e, fcivec, norb, nelec, link_index)
    return numpy.dot(fcivec.reshape(-1), ci1.reshape(-1))


# dm_pq = <|p^+ q|>
def make_rdm1s(fcivec, norb, nelec, link_index=None):
    if link_index is None:
        link_indexa = cistring.gen_linkstr_index(range(norb), nelec[0])
        link_indexb = cistring.gen_linkstr_index(range(norb), nelec[1])
        link_index = (link_indexa, link_indexb)
    rdm1a = rdm.make_rdm1_spin1('FCImake_rdm1a', fcivec, fcivec,
                                norb, nelec, link_index)
    rdm1b = rdm.make_rdm1_spin1('FCImake_rdm1b', fcivec, fcivec,
                                norb, nelec, link_index)
    return rdm1a, rdm1b

# spacial part of DM, dm_pq = <|p^+ q|>
def make_rdm1(fcivec, norb, nelec, link_index=None):
    rdm1a, rdm1b = make_rdm1s(fcivec, norb, nelec, link_index)
    return rdm1a + rdm1b

def make_rdm12s(fcivec, norb, nelec, link_index=None):
    dm1a, dm2aa = rdm.make_rdm12_spin1('FCIrdm12kern_a', fcivec, fcivec,
                                       norb, nelec, link_index, 1)
    dm1b, dm2bb = rdm.make_rdm12_spin1('FCIrdm12kern_b', fcivec, fcivec,
                                       norb, nelec, link_index, 1)
    _, dm2ab = rdm.make_rdm12_spin1('FCItdm12kern_ab', fcivec, fcivec,
                                    norb, nelec, link_index, 0)
    dm1a, dm2aa = rdm.reorder_rdm(dm1a, dm2aa, inplace=True)
    dm1b, dm2bb = rdm.reorder_rdm(dm1b, dm2bb, inplace=True)
    return (dm1a, dm1b), (dm2aa, dm2ab, dm2bb)

def make_rdm12(fcivec, norb, nelec, link_index=None):
    (dm1a, dm1b), (dm2aa, dm2ab, dm2bb) = \
            make_rdm12s(fcivec, norb, nelec, link_index)
    return dm1a+dm1b, dm2aa+dm2ab+dm2ab.transpose(2,3,0,1)+dm2bb

def trans_rdm1s(cibra, ciket, norb, nelec, link_index=None):
    rdm1a = rdm.make_rdm1_spin1('FCItrans_rdm1a', cibra, ciket,
                                norb, nelec, link_index)
    rdm1b = rdm.make_rdm1_spin1('FCItrans_rdm1b', cibra, ciket,
                                norb, nelec, link_index)
    return rdm1a, rdm1b

# spacial part of DM
def trans_rdm1(cibra, ciket, norb, nelec, link_index=None):
    rdm1a, rdm1b = trans_rdm1s(cibra, ciket, norb, nelec, link_index)
    return rdm1a + rdm1b

def trans_rdm12s(cibra, ciket, norb, nelec, link_index=None):
    dm1a, dm2aa = rdm.make_rdm12_spin1('FCItdm12kern_a', cibra, ciket,
                                       norb, nelec, link_index, 0)
    dm1b, dm2bb = rdm.make_rdm12_spin1('FCItdm12kern_b', cibra, ciket,
                                       norb, nelec, link_index, 0)
    _, dm2ab = rdm.make_rdm12_spin1('FCItdm12kern_ab', cibra, ciket,
                                    norb, nelec, link_index, 0)
    _, dm2ba = rdm.make_rdm12_spin1('FCItdm12kern_ab', ciket, cibra,
                                    norb, nelec, link_index, 0)
    dm2ba = dm2ba.transpose(3,2,1,0)
    dm1a, dm2aa = rdm.reorder_rdm(dm1a, dm2aa, inplace=True)
    dm1b, dm2bb = rdm.reorder_rdm(dm1b, dm2bb, inplace=True)
    return (dm1a, dm1b), (dm2aa, dm2ab, dm2ba, dm2bb)

def trans_rdm12(cibra, ciket, norb, nelec, link_index=None):
    (dm1a, dm1b), (dm2aa, dm2ab, dm2ba, dm2bb) = \
            trans_rdm12s(cibra, ciket, norb, nelec, link_index)
    return dm1a+dm1b, dm2aa+dm2ab+dm2ba+dm2bb

