#include <stdlib.h>
#include <string.h>
#include <omp.h>

#if defined SCIPY_MKL_H
typedef long FINT;
#else
typedef int FINT;
#endif

static void ci_misc_unpack(unsigned int n, double *vec, double *mat)
{
        unsigned int i, j;
        for (i = 0; i < n; i++) {
                for (j = 0; j <= i; j++, vec++) {
                        mat[i*n+j] = *vec;
                        mat[j*n+i] = *vec;
                }
        }
}


/* eri uses 4-fold symmetry: i>=j,k>=l */
void ci_misc_half_trans_o2(int nao, int nmo, double *eri, double *c,
                           double *mat)
{
        const double D0 = 0;
        const double D1 = 1;
        const char TRANS_T = 'T';
        const char TRANS_N = 'N';
        const FINT lao = nao;
        const FINT lmo = nmo;
        unsigned int i, j;
        double *tmp1 = malloc(sizeof(double)*nao*nao);
        double *tmp2 = malloc(sizeof(double)*nao*nmo);
        ci_misc_unpack(nao, eri, tmp1);
        dgemm_(&TRANS_N, &TRANS_N, &lao, &lmo, &lao,
               &D1, tmp1, &lao, c, &lao, &D0, tmp2, &lao);
        dgemm_(&TRANS_T, &TRANS_N, &lmo, &lmo, &lao,
               &D1, c, &lao, tmp2, &lao, &D0, tmp1, &lmo);

        for (i = 0; i < nmo; i++) {
                for (j = 0; j <= i; j++, mat++) {
                        *mat = tmp1[i*nmo+j];
                }
        }
        free(tmp1);
        free(tmp2);
}

static void extract_row_from_tri_eri(double *row, unsigned int row_id,
                                     double *eri, unsigned int npair)
{
        unsigned long idx;
        unsigned int i;
        idx = (unsigned long)row_id * (row_id + 1) / 2;
        memcpy(row, eri+idx, sizeof(double)*row_id);
        for (i = row_id; i < npair; i++) {
                idx += i;
                row[i] = eri[idx];
        }
}


/* eri uses 8-fold symmetry: i>=j,k>=l,ij>=kl */
void ci_misc_half_trans_o3(int nao, int nmo, int pair_id,
                           double *eri, double *c, double *mat)
{
        const double D0 = 0;
        const double D1 = 1;
        const char TRANS_T = 'T';
        const char TRANS_N = 'N';
        const FINT lao = nao;
        const FINT lmo = nmo;
        unsigned int i, j;
        unsigned int nao_pair = nao * (nao+1) / 2;
        double *row = malloc(sizeof(double)*nao_pair);
        double *tmp1 = malloc(sizeof(double)*nao*nao);
        double *tmp2 = malloc(sizeof(double)*nao*nmo);

        extract_row_from_tri_eri(row, pair_id, eri, nao_pair);
        ci_misc_unpack(nao, row, tmp1);
        dgemm_(&TRANS_N, &TRANS_N, &lao, &lmo, &lao,
               &D1, tmp1, &lao, c, &lao, &D0, tmp2, &lao);
        dgemm_(&TRANS_T, &TRANS_N, &lmo, &lmo, &lao,
               &D1, c, &lao, tmp2, &lao, &D0, tmp1, &lmo);

        for (i = 0; i < nmo; i++) {
                for (j = 0; j <= i; j++, mat++) {
                        *mat = tmp1[i*nmo+j];
                }
        }
        free(row);
        free(tmp1);
        free(tmp2);
}
