#!/usr/bin/env python

import sys
import os
import cPickle
import csv

import numpy as np
from scipy.sparse import csr_matrix

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
    fp = open(filename, 'r')
    reader = csv.reader(fp, delimiter=',')
    meta = reader.next()
    N = int(meta[0])
    M = int(meta[1])
    
    rows = []
    cols = []
    vals = []
    
    n = 0
    m = 0
    
    tz = time.time()
    it = 0
    for line in reader:
        if it > 1 and it % 5000000 == 0:
            print "Progress %dM" % (it / 1000000)
        i, j, r = int(line[0]), int(line[1]), float(line[2])
        if r < 0:
            r = 0
        if i > n:
            n = i
        if j > m:
            m = j
        rows.append(i)
        cols.append(j)
        vals.append(r)
        it += 1
    
    fp.close()
    n = n+1
    m = m+1

    print N, n
    print M, m
    
    n, m = N, M
    
    t0 = time.time()
    print 'Read in: ', t0-tz
    data = np.array(vals, dtype=np.float32)
    X = csr_matrix((vals,(rows,cols)),shape=(n, m),dtype=np.float32)
    t1 = time.time()
    print 'Constructed in: ', t1-t0
    
    save_numpy(pklname, X)
    t2 = time.time()
    print 'Dumped in: ', t2-t1

def csv_todense(filename, pklname):
    fp = open(filename, 'r')
    reader = csv.reader(fp, delimiter=',')
    meta = reader.next()
    n = int(meta[0])
    m = int(meta[1])
    
    t0 = time.time()
    X = np.zeros((n,m), dtype=np.float32)
    it = 0
    for line in reader:
        if it > 1 and it % 5000000 == 0:
            print "Progress %dM" % (it / 1000000)
        i, j, r = int(line[0]), int(line[1]), float(line[2])
        if r < 0:
            r = 0
        X[i,j] = r
        it += 1
    
    fp.close()
    t1 = time.time()
    print 'Constructed in: ', t1-t0
    print pklname, X.shape
    save_numpy(pklname, X)
    t2 = time.time()
    print 'Dumped in: ', t2-t1
    

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

def csv_to_bio(data_file, output_file):
    fp = open(data_file, 'r')
    reader = csv.reader(fp, delimiter=',')
    meta = reader.next()
    n = int(meta[0])
    m = int(meta[1])
    
    t0 = time.time()
    X = np.zeros((n,m), dtype=np.float32)
    it = 0
    for line in reader:
        if it > 1 and it % 5000000 == 0:
            print "Progress %dM" % (it / 1000000)
        i, j, r = int(line[0]), int(line[1]), float(line[2])
        if r < 0:
            r = 0
        X[i,j] = r
        it += 1
    
    fp.close()
    t1 = time.time()
    print 'Constructed in: ', t1-t0
    
    fp = open(output_file, 'w')
    writer = csv.writer(fp, delimiter='\t')
    
    for i in range(n):
        writer.writerow(X[i,:])
    
    fp.close()
    
    t2 = time.time()
    print 'Dumped in: ', t2-t1

def test(data_file):
    csv_dataset_to_blocks(data_file)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 2:
        print "Provide path to one data file and one output file"
        sys.exit()
    data_file = args[0]
    output_file = args[1]
    csv_to_bio(data_file, output_file)