/*
 *
 */

#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <math.h>
#include <complex.h>
//#include <omp.h>
#include "config.h"
#include "cint.h"
#include "optimizer.h"
#include "nr_direct.h"
#include "time_rev.h"


static void transpose01324(double complex * __restrict__ a,
                           double complex * __restrict__ at,
                           int di, int dj, int dk, int dl, int ncomp)
{
        int i, j, k, l, m, ic;
        int dij = di * dj;
        int dijk = dij * dk;
        double complex *pa;

        m = 0;
        for (ic = 0; ic < ncomp; ic++) {
                for (l = 0; l < dl; l++) {
                        for (j = 0; j < dj; j++) {
                                pa = a + j*di;
                                for (k = 0; k < dk; k++) {
                                        for (i = 0; i < di; i++) {
                                                at[m] = pa[i];
                                                m++;
                                        }
                                        pa += dij;
                                }
                        }
                        a += dijk;
                }
        }
}
/*
 * for given ksh, lsh, loop all ish, jsh
 */
void CVHFdot_rs1(int (*intor)(), void (**fjk)(),
                 double complex **dms, double complex *vjk,
                 int n_dm, int ncomp, int ish, int jsh,
                 CINTOpt *cintopt, CVHFOpt *vhfopt, struct _VHFEnvs *envs)
{
        const int nao = envs->nao;
        const int nao2 = nao * nao;
        const int *ao_loc = envs->ao_loc;
        const int *tao = envs->tao;
        const int di = ao_loc[ish+1] - ao_loc[ish];
        const int dj = ao_loc[jsh+1] - ao_loc[jsh];
        int idm;
        int ksh, lsh, dk, dl, dijkl;
        int shls[4];
        double complex *buf;
        double complex *pv;
        double *dms_cond[n_dm];
        double dm_atleast;
        void (*pf)();
        int (*fprescreen)();
        int (*r_vkscreen)();

        if (vhfopt) {
                fprescreen = vhfopt->fprescreen;
                r_vkscreen = vhfopt->r_vkscreen;
        } else {
                fprescreen = CVHFnoscreen;
                r_vkscreen = CVHFr_vknoscreen;
        }

// to make fjk compatible to C-contiguous dm array, put ksh, lsh inner loop
        shls[0] = ish;
        shls[1] = jsh;

        for (ksh = 0; ksh < envs->nbas; ksh++) {
        for (lsh = 0; lsh < envs->nbas; lsh++) {
                dk = ao_loc[ksh+1] - ao_loc[ksh];
                dl = ao_loc[lsh+1] - ao_loc[lsh];
                shls[2] = ksh;
                shls[3] = lsh;
                if ((*fprescreen)(shls, vhfopt,
                                  envs->atm, envs->bas, envs->env)) {
// append buf.transpose(0,2,1,3) to eris, to reduce the cost of r_direct_dot
                        dijkl = di * dj * dk * dl;
                        buf = malloc(sizeof(double complex) * dijkl*ncomp*2);
                        if ((*intor)(buf, shls, envs->atm, envs->natm,
                                     envs->bas, envs->nbas, envs->env,
                                     cintopt)) {
                                if ((*r_vkscreen)(shls, vhfopt,
                                                  dms_cond, n_dm, &dm_atleast,
                                                  envs->atm, envs->bas, envs->env)) {
                                        transpose01324(buf, buf+dijkl*ncomp,
                                                       di, dj, dk, dl, ncomp);
                                }
                                pv = vjk;
                                for (idm = 0; idm < n_dm; idm++) {
                                        pf = fjk[idm];
                                        (*pf)(buf, dms[idm], pv, nao, ncomp,
                                              shls, ao_loc, tao,
                                              dms_cond[idm], envs->nbas, dm_atleast);
                                        pv += nao2 * ncomp;
                                }
                        }
                        free(buf);
                }
        } }
}

/*
 * for given ish, jsh, loop all ksh > lsh
 */
static void dot_rs2sub(int (*intor)(), void (**fjk)(),
                       double complex **dms, double complex *vjk,
                       int n_dm, int ncomp, int ish, int jsh, int ksh_count,
                       CINTOpt *cintopt, CVHFOpt *vhfopt,
                       struct _VHFEnvs *envs)
{
        const int nao = envs->nao;
        const int nao2 = nao * nao;
        const int *ao_loc = envs->ao_loc;
        const int *tao = envs->tao;
        const int di = ao_loc[ish+1] - ao_loc[ish];
        const int dj = ao_loc[jsh+1] - ao_loc[jsh];
        int idm;
        int ksh, lsh, dk, dl, dijkl;
        int shls[4];
        double complex *buf;
        double complex *pv;
        double *dms_cond[n_dm];
        double dm_atleast;
        void (*pf)();
        int (*fprescreen)();
        int (*r_vkscreen)();

        if (vhfopt) {
                fprescreen = vhfopt->fprescreen;
                r_vkscreen = vhfopt->r_vkscreen;
        } else {
                fprescreen = CVHFnoscreen;
                r_vkscreen = CVHFr_vknoscreen;
        }

        shls[0] = ish;
        shls[1] = jsh;

        for (ksh = 0; ksh < ksh_count; ksh++) {
        for (lsh = 0; lsh <= ksh; lsh++) {
                dk = ao_loc[ksh+1] - ao_loc[ksh];
                dl = ao_loc[lsh+1] - ao_loc[lsh];
                shls[2] = ksh;
                shls[3] = lsh;
                if ((*fprescreen)(shls, vhfopt,
                                  envs->atm, envs->bas, envs->env)) {
                        dijkl = di * dj * dk * dl;
                        buf = malloc(sizeof(double complex) * dijkl*ncomp*2);
                        if ((*intor)(buf, shls, envs->atm, envs->natm,
                                     envs->bas, envs->nbas, envs->env,
                                     cintopt)) {
                                if ((*r_vkscreen)(shls, vhfopt,
                                                  dms_cond, n_dm, &dm_atleast,
                                                  envs->atm, envs->bas, envs->env)) {
                                        transpose01324(buf, buf+dijkl*ncomp,
                                                       di, dj, dk, dl, ncomp);
                                }
                                pv = vjk;
                                for (idm = 0; idm < n_dm; idm++) {
                                        pf = fjk[idm];
                                        (*pf)(buf, dms[idm], pv, nao, ncomp,
                                              shls, ao_loc, tao,
                                              dms_cond[idm], envs->nbas, dm_atleast);
                                        pv += nao2 * ncomp;
                                }
                        }
                        free(buf);
                }
        } }
}

void CVHFdot_rs2ij(int (*intor)(), void (**fjk)(),
                   double complex **dms, double complex *vjk,
                   int n_dm, int ncomp, int ish, int jsh,
                   CINTOpt *cintopt, CVHFOpt *vhfopt, struct _VHFEnvs *envs)
{
        if (ish >= jsh) {
                CVHFdot_rs1(intor, fjk, dms, vjk, n_dm, ncomp,
                            ish, jsh, cintopt, vhfopt, envs);
        }
}

void CVHFdot_rs2kl(int (*intor)(), void (**fjk)(),
                   double complex **dms, double complex *vjk,
                   int n_dm, int ncomp, int ish, int jsh,
                   CINTOpt *cintopt, CVHFOpt *vhfopt, struct _VHFEnvs *envs)
{
        dot_rs2sub(intor, fjk, dms, vjk, n_dm, ncomp,
                   ish, jsh, envs->nbas, cintopt, vhfopt, envs);
}

void CVHFdot_rs4(int (*intor)(), void (**fjk)(),
                 double complex **dms, double complex *vjk,
                 int n_dm, int ncomp, int ish, int jsh,
                 CINTOpt *cintopt, CVHFOpt *vhfopt, struct _VHFEnvs *envs)
{
        if (ish >= jsh) {
                dot_rs2sub(intor, fjk, dms, vjk, n_dm, ncomp,
                           ish, jsh, envs->nbas, cintopt, vhfopt, envs);
        }
}

void CVHFdot_rs8(int (*intor)(), void (**fjk)(),
                 double complex **dms, double complex *vjk,
                 int n_dm, int ncomp, int ish, int jsh,
                 CINTOpt *cintopt, CVHFOpt *vhfopt, struct _VHFEnvs *envs)
{
        if (ish < jsh) {
                return;
        }
        const int nao = envs->nao;
        const int nao2 = nao * nao;
        const int *ao_loc = envs->ao_loc;
        const int *tao = envs->tao;
        const int di = ao_loc[ish+1] - ao_loc[ish];
        const int dj = ao_loc[jsh+1] - ao_loc[jsh];
        int idm;
        int ksh, lsh, dk, dl, dijkl;
        int shls[4];
        double complex *buf;
        double complex *pv;
        double *dms_cond[n_dm];
        double dm_atleast;
        void (*pf)();
        int (*fprescreen)();
        int (*r_vkscreen)();

        if (vhfopt) {
                fprescreen = vhfopt->fprescreen;
                r_vkscreen = vhfopt->r_vkscreen;
        } else {
                fprescreen = CVHFnoscreen;
                r_vkscreen = CVHFr_vknoscreen;
        }

// to make fjk compatible to C-contiguous dm array, put ksh, lsh inner loop
        shls[0] = ish;
        shls[1] = jsh;

        for (ksh = 0; ksh <= ish; ksh++) {
        for (lsh = 0; lsh <= ksh; lsh++) {
/* when ksh==ish, (lsh<jsh) misses some integrals (eg k<i&&l>j).
 * These integrals are calculated in the next (ish,jsh) pair. To show
 * that, we just need to prove that every elements in shell^4 appeared
 * only once in fjk_s8.  */
                if ((ksh == ish) && (lsh > jsh)) {
                        break;
                }
                dk = ao_loc[ksh+1] - ao_loc[ksh];
                dl = ao_loc[lsh+1] - ao_loc[lsh];
                shls[2] = ksh;
                shls[3] = lsh;
                if ((*fprescreen)(shls, vhfopt,
                                  envs->atm, envs->bas, envs->env)) {
                        dijkl = di * dj * dk * dl;
                        buf = malloc(sizeof(double complex) * dijkl*ncomp*2);
                        if ((*intor)(buf, shls, envs->atm, envs->natm,
                                     envs->bas, envs->nbas, envs->env,
                                     cintopt)) {
                                if ((*r_vkscreen)(shls, vhfopt,
                                                  dms_cond, n_dm, &dm_atleast,
                                                  envs->atm, envs->bas, envs->env)) {
                                        transpose01324(buf, buf+dijkl*ncomp,
                                                       di, dj, dk, dl, ncomp);
                                }
                                pv = vjk;
                                for (idm = 0; idm < n_dm; idm++) {
                                        pf = fjk[idm];
                                        (*pf)(buf, dms[idm], pv, nao, ncomp,
                                              shls, ao_loc, tao,
                                              dms_cond[idm], envs->nbas, dm_atleast);
                                        pv += nao2 * ncomp;
                                }
                        }
                        free(buf);
                }
        } }
}

/*
 * drv loop over ij, generate eris of kl for given ij, call fjk to
 * calculate vj, vk.
 * 
 * n_dm is the number of dms for one [array(ij|kl)],
 * ncomp is the number of components that produced by intor
 */
void CVHFr_direct_drv(int (*intor)(), void (*fdot)(), void (**fjk)(),
                      double complex **dms, double complex *vjk,
                      int n_dm, int ncomp, CINTOpt *cintopt, CVHFOpt *vhfopt,
                      int *atm, int natm, int *bas, int nbas, double *env)
{
        const int nao = CINTtot_cgto_spinor(bas, nbas);
        int *ao_loc = malloc(sizeof(int)*(nbas+1));
        int *tao = malloc(sizeof(int)*nao);
        struct _VHFEnvs envs = {natm, nbas, atm, bas, env, nao, ao_loc, tao};

        memset(vjk, 0, sizeof(double complex)*nao*nao*n_dm*ncomp);
        CINTshells_spinor_offset(ao_loc, bas, nbas);
        ao_loc[nbas] = nao;
        CVHFtimerev_map(tao, bas, nbas);

#pragma omp parallel default(none) \
        shared(intor, fdot, fjk, \
               dms, vjk, n_dm, ncomp, nbas, cintopt, vhfopt, envs)
        {
                int i, j, ij;
                double complex *v_priv = malloc(sizeof(double complex)*nao*nao*n_dm*ncomp);
                memset(v_priv, 0, sizeof(double complex)*nao*nao*n_dm*ncomp);
#pragma omp for nowait schedule(dynamic)
                for (ij = 0; ij < nbas*nbas; ij++) {
                        i = ij / nbas;
                        j = ij - i * nbas;
                        (*fdot)(intor, fjk, dms, v_priv, n_dm, ncomp, i, j,
                                cintopt, vhfopt, &envs);
                }
#pragma omp critical
                {
                        for (i = 0; i < nao*nao*n_dm*ncomp; i++) {
                                vjk[i] += v_priv[i];
                        }
                }
                free(v_priv);
        }

        free(ao_loc);
        free(tao);
}

