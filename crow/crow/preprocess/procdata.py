#!/usr/bin/env python

import sys
import os
import cPickle
import csv

import numpy as np
from scipy.sparse import csr_matrix

from crow.convert.csv import load_coo, load_coo_sparse
from crow.utils import *

def dummy_partition(X, nb, mb):
    n, m = X.shape
    islices = [(i*n//nb, (i+1)*n//nb) for i in range(nb)]
    jslices = [(i*m//mb, (i+1)*m//mb) for i in range(mb)]
    R = [[X[a:b,c:d] for c,d in jslices] for a,b in islices]
    return R

def balanced_partition(X, nb, mb):
    rows = X.getnnz(1)
    cols = X.getnnz(0)
    nnz = X.getnnz()
    print 'Shape', X.shape, 'Nonzero %.2fM' % (float(nnz)/1000000)
    rows = np.cumsum(rows).astype(np.int)
    cols = np.cumsum(cols).astype(np.int)
    limits = [i*nnz/nb for i in range(nb+1)]
    
    p = 1
    idx_list = [0]
    for i in range(len(rows)):
        if rows[i] >= limits[p]:
            idx_list.append(i+1)
            p += 1
    
    limits = [j*nnz/mb for j in range(mb+1)]
    
    p = 1
    jdx_list = [0]
    for j in range(len(cols)):
        if cols[j] >= limits[p]:
            jdx_list.append(j+1)
            p += 1
    
    islices = [(idx_list[i], idx_list[i+1]) for i in range(nb)]
    jslices = [(jdx_list[j], jdx_list[j+1]) for j in range(mb)]
    
    R = [[X[a:b,c:d] for c,d in jslices] for a,b in islices]
    
    stat = {}
    for i in range(nb):
        for j in range(mb):
            z = R[i][j].getnnz()
            stat[(i,j)] = float(z)/nnz
    
    print sorted(stat.items(), key=lambda x: x[0])
    return R, islices, jslices

def slice_datasets(input_file, output_folder, blocks=[]):
    for nb, mb in blocks:
        output_folder = to_path(output_folder, '%d_%d' % (nb, mb))
        X = load_numpy(input_file)
        X = dummy_partition(X, nb, mb)
        for i in range(nb):
            for j in range(mb):
                output_file = to_path(output_folder, '%d_%d.npz' % (i, j))
                save_numpy(output_file, X[i][j])

def balanced_slicing(input_file, output_folder, blocks=[]):
    # Sparse only
    S = load_numpy(input_file)
    for nb, mb in blocks:
        blockfolder = to_path(output_folder, '%d_%d' % (nb, mb))
        X, islices, jslices = balanced_partition(S, nb, mb)
        for i in range(nb):
            for j in range(mb):
                output_file = to_path(blockfolder, '%d_%d.npz' % (i, j))
                save_numpy(output_file, X[i][j])
                #meta_file = to_path(blockfolder, 'meta.pkl')
                #dump_file(meta_file, (islices, jslices))

def unbalanced_slicing(input_file, output_folder, blocks=[]):
    # Sparse only
    S = load_numpy(input_file)
    for nb, mb in blocks:
        blockfolder = to_path(output_folder, 'u%d_%d' % (nb, mb))
        X = dummy_partition(S, nb, mb)
        for i in range(nb):
            for j in range(mb):
                output_file = to_path(blockfolder, '%d_%d.npz' % (i, j))
                save_numpy(output_file, X[i][j])
                #meta_file = to_path(blockfolder, 'meta.pkl')
                #dump_file(meta_file, (islices, jslices))


def csv_tosparse_fast(filename, pklname):
    X = load_coo_sparse(filename, verbose=True)
    save_numpy(pklname, X)
    
def csv_todense(filename, pklname):
    load_coo(filename, verbose=True)
    save_numpy(pklname, X)

def dense_dataset_to_blocks(data_file, data_folder, blocks=[(2,1),(4,1)]):
    pkl_sparse = to_path(data_folder, '1_1', '0_0.npz')
    if not os.path.isfile(pkl_sparse):
        csv_todense(data_file, pkl_sparse)
    
    slice_datasets(pkl_sparse, data_folder, blocks=blocks)
    return data_folder

def sparse_dataset_to_blocks(data_file, data_folder, blocks=[(2,1),(4,1)], balanced=True):
    pkl_sparse = to_path(data_folder, '1_1', '0_0.npz')
    if not os.path.isfile(pkl_sparse):
        csv_tosparse_fast(data_file, pkl_sparse)
    
    if balanced == True:
        balanced_slicing(pkl_sparse, data_folder, blocks=blocks)
    else:
        unbalanced_slicing(pkl_sparse, data_folder, blocks=blocks)
    return data_folder

def dataset_to_blocks(data_file, cache_folder, blocks=[(2,1),(4,1)], sparse=False, balanced=True):
    if sparse == False:
        return dense_dataset_to_blocks(data_file, cache_folder, blocks=blocks)
    else:
        return sparse_dataset_to_blocks(data_file, cache_folder, blocks=blocks, balanced=balanced)


def test(data_file):
    csv_dataset_to_blocks(data_file)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 2:
        print "Provide path to one data file and one output file"
        sys.exit()