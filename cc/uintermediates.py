import tempfile
import h5py
import numpy as np

from pyscf.pbc import lib as pbclib
from pyscf.cc.ccsd import _cp

#einsum = np.einsum
einsum = pbclib.einsum

# Ref: Gauss and Stanton, J. Chem. Phys. 103, 3561 (1995) Table III

# Section (a)

def make_tau(t2, t1a, t1b, fac=1, out=None):
    tmp = einsum('ia,jb->ijab',t1a,t1b)
    t1t1 = tmp - tmp.transpose(1,0,2,3) - tmp.transpose(0,1,3,2) + tmp.transpose(1,0,3,2)
    tau1 = t2 + fac*0.50*t1t1
    return tau1

def cc_Fvv(t1,t2,eris):
    nocc, nvir = t1.shape
    fov = eris.fock[:nocc,nocc:]
    fvv = eris.fock[nocc:,nocc:]
    eris_vovv = _cp(eris.ovvv).transpose(1,0,3,2)
    tau_tilde = make_tau(t2,t1,t1,fac=0.5)
    Fae = ( fvv - 0.5*einsum('me,ma->ae',fov,t1)
            + einsum('mf,amef->ae',t1,eris_vovv)
            - 0.5*einsum('mnaf,mnef->ae',tau_tilde,eris.oovv) )
    return Fae

def cc_Foo(t1,t2,eris):
    nocc, nvir = t1.shape
    fov = eris.fock[:nocc,nocc:]
    foo = eris.fock[:nocc,:nocc]
    tau_tilde = make_tau(t2,t1,t1,fac=0.5)
    Fmi = ( foo + 0.5*einsum('me,ie->mi',fov,t1) 
            + einsum('ne,mnie->mi',t1,eris.ooov)
            + 0.5*einsum('inef,mnef->mi',tau_tilde,eris.oovv) )
    return Fmi

def cc_Fov(t1,t2,eris):
    nocc, nvir = t1.shape
    Fme = einsum('nf,mnef->me',t1,eris.oovv)
    return Fme

def cc_Woooo(t1,t2,eris):
    tau = make_tau(t2,t1,t1)
    tmp = einsum('je,mnie->mnij',t1,eris.ooov)
    Wmnij = eris.oooo + tmp - tmp.transpose(0,1,3,2)
    Wmnij += 0.25*einsum('ijef,mnef->mnij',tau,eris.oovv)
    return Wmnij

def cc_Wvvvv(t1,t2,eris):
    #eris_vovv = _cp(eris.ovvv).transpose(1,0,3,2)
    tau = make_tau(t2,t1,t1)
    #tmp = einsum('mb,amef->abef',t1,eris_vovv)
    #Wabef = eris.vvvv - tmp + tmp.transpose(1,0,2,3)
    #Wabef += 0.25*einsum('mnab,mnef->abef',tau,eris.oovv)
    if t1.dtype == np.complex: ds_type = 'c16'
    else: ds_type = 'f8'
    _tmpfile1 = tempfile.NamedTemporaryFile()
    fimd = h5py.File(_tmpfile1.name)
    nocc, nvir = t1.shape
    Wabef = fimd.create_dataset('vvvv', (nvir,nvir,nvir,nvir), ds_type)
    for a in range(nvir):
        #tmp = einsum('mb,mef->bef',t1,eris_vovv[a])
        #tmp_tr = einsum('m,bmef->bef',t1[:,a],eris_vovv)
        tmp = einsum('mb,mfe->bef',t1,eris.ovvv[:,a,:])
        tmp_tr = einsum('m,mbfe->bef',t1[:,a],eris.ovvv)
        Wabef[a] = eris.vvvv[a] - tmp[:] + tmp_tr[:]
        Wabef[a] += 0.25*einsum('mnb,mnef->bef',tau[:,:,a,:],eris.oovv)
    return Wabef

def cc_Wovvo(t1,t2,eris):
    eris_ovvo = - _cp(eris.ovov).transpose(0,1,3,2)
    eris_oovo = - _cp(eris.ooov).transpose(0,1,3,2)
    Wmbej = eris_ovvo.copy()
    Wmbej +=  einsum('jf,mbef->mbej',t1,eris.ovvv)
    Wmbej += -einsum('nb,mnej->mbej',t1,eris_oovo)
    Wmbej += -0.5*einsum('jnfb,mnef->mbej',t2,eris.oovv)
    Wmbej += -einsum('jf,nb,mnef->mbej',t1,t1,eris.oovv)
    return Wmbej

### Section (b)

def Fvv(t1,t2,eris):
    ccFov = cc_Fov(t1,t2,eris)
    Fae = cc_Fvv(t1,t2,eris) - 0.5*einsum('ma,me->ae',t1,ccFov)
    return Fae

def Foo(t1,t2,eris):
    ccFov = cc_Fov(t1,t2,eris)
    Fmi = cc_Foo(t1,t2,eris) + 0.5*einsum('ie,me->mi',t1,ccFov)
    return Fmi

def Fov(t1,t2,eris):
    Fme = cc_Fov(t1,t2,eris)
    return Fme

def Woooo(t1,t2,eris):
    tau = make_tau(t2,t1,t1)
    Wmnij = cc_Woooo(t1,t2,eris) + 0.25*einsum('ijef,mnef->mnij',tau,eris.oovv)
    return Wmnij

def Wvvvv(t1,t2,eris):
    tau = make_tau(t2,t1,t1)
    #Wabef = cc_Wvvvv(t1,t2,eris) + 0.25*einsum('mnab,mnef->abef',tau,eris.oovv)
    if t1.dtype == np.complex: ds_type = 'c16'
    else: ds_type = 'f8'
    _tmpfile1 = tempfile.NamedTemporaryFile()
    fimd = h5py.File(_tmpfile1.name)
    nocc, nvir = t1.shape
    Wabef = fimd.create_dataset('vvvv', (nvir,nvir,nvir,nvir), ds_type)
    for a in range(nvir):
        #TODO: Wasteful to create cc_Wvvvv twice
        Wabef[a] = cc_Wvvvv(t1,t2,eris)[a]
        Wabef[a] += 0.25*einsum('mnb,mnef->bef',tau[:,:,a,:],eris.oovv) 
    return Wabef

def Wovvo(t1,t2,eris):
    Wmbej = cc_Wovvo(t1,t2,eris) - 0.5*einsum('jnfb,mnef->mbej',t2,eris.oovv)
    return Wmbej

# Indices in the following can be safely permuted.

def Wooov(t1,t2,eris):
    Wmnie = eris.ooov + einsum('if,mnfe->mnie',t1,eris.oovv)
    return Wmnie

def Wvovv(t1,t2,eris):
    eris_vovv = - _cp(eris.ovvv).transpose(1,0,2,3)
    Wamef = eris_vovv - einsum('na,nmef->amef',t1,eris.oovv)
    return Wamef

def Wovoo(t1,t2,eris):
    eris_ovvo = - _cp(eris.ovov).transpose(0,1,3,2)
    tmp1 = einsum('mnie,jnbe->mbij',eris.ooov,t2)
    tmp2 = ( einsum('ie,mbej->mbij',t1,eris_ovvo)
            - einsum('ie,njbf,mnef->mbij',t1,t2,eris.oovv) )
    FFov = Fov(t1,t2,eris)
    WWoooo = Woooo(t1,t2,eris)
    tau = make_tau(t2,t1,t1)
    Wmbij = ( eris.ovoo - einsum('me,ijbe->mbij',FFov,t2)
              - einsum('nb,mnij->mbij',t1,WWoooo)
              + 0.5 * einsum('mbef,ijef->mbij',eris.ovvv,tau)
              + tmp1 - tmp1.transpose(0,1,3,2)
              + tmp2 - tmp2.transpose(0,1,3,2) )
    return Wmbij

def Wvvvo(t1,t2,eris):
    eris_ovvo = - _cp(eris.ovov).transpose(0,1,3,2)
    eris_vvvo = - _cp(eris.ovvv).transpose(2,3,1,0).conj()
    eris_oovo = - _cp(eris.ooov).transpose(0,1,3,2)
    tmp1 = einsum('mbef,miaf->abei',eris.ovvv,t2)
    tmp2 = ( einsum('ma,mbei->abei',t1,eris_ovvo)
            - einsum('ma,nibf,mnef->abei',t1,t2,eris.oovv) )
    FFov = Fov(t1,t2,eris)
    tau = make_tau(t2,t1,t1)
    Wabei = eris_vvvo 
    Wabei += -einsum('me,miab->abei',FFov,t2)
    Wabei += 0.5 * einsum('mnei,mnab->abei',eris_oovo,tau)
    Wabei += -tmp1 + tmp1.transpose(1,0,2,3)
    Wabei += -tmp2 + tmp2.transpose(1,0,2,3) 
    nocc,nvir = t1.shape
    for a in range(nvir):
        #TODO: Wasteful to create Wvvvv twice (now cc_Wvvvv three times!)
        Wabei[a] += einsum('if,bef->bei',t1,Wvvvv(t1,t2,eris)[a])
    return Wabei

def Wvvvo_incore(t1,t2,eris):
    eris_ovvo = - _cp(eris.ovov).transpose(0,1,3,2)
    eris_vvvo = - _cp(eris.ovvv).transpose(2,3,1,0).conj()
    eris_oovo = - _cp(eris.ooov).transpose(0,1,3,2)
    tmp1 = einsum('mbef,miaf->abei',eris.ovvv,t2)
    tmp2 = ( einsum('ma,mbei->abei',t1,eris_ovvo)
            - einsum('ma,nibf,mnef->abei',t1,t2,eris.oovv) )
    FFov = Fov(t1,t2,eris)
    #TODO: Wasteful to create Wvvvv twice (now cc_Wvvvv three times!)
    WWvvvv = Wvvvv(t1,t2,eris)
    tau = make_tau(t2,t1,t1)
    Wabei = ( eris_vvvo - einsum('me,miab->abei',FFov,t2)
                    + einsum('if,abef->abei',t1,WWvvvv)
                    + 0.5 * einsum('mnei,mnab->abei',eris_oovo,tau)
                    - tmp1 + tmp1.transpose(1,0,2,3)
                    - tmp2 + tmp2.transpose(1,0,2,3) )
    return Wabei
