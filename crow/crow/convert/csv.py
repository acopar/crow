import sys
import os
import csv
import time

import numpy as np
from crow.utils import *

def load_csv(filename, delimiter=','):
    # loads csv file into array of rows (arrays)
    csv.field_size_limit(sys.maxsize)
    fp = open(filename)
    if not fp:
        print "Error: Cannot open file: %s" % filename
        return None
    
    reader = csv.reader(fp, delimiter=delimiter)
    data = []
    for row in reader:
        data.append(row)
    fp.close()
    return data

def save_csv(filename, data, delimiter=',', append=False):
    # write csv file (arrays)
    ensure_dir(filename)
    if append:
        fp = open(filename, 'a')
    else:
        fp = open(filename, 'w')
    
    if not fp:
        print "Error: Cannot open file: %s" % filename
        return None
    
    writer = csv.writer(fp, delimiter=delimiter)
    for line in data:
        writer.writerow(line)
    fp.close()

def write_coo(filename, X):
    fp = open(filename, 'w')
    writer = csv.writer(fp, delimiter=',')
    n = X.shape[0]
    m = X.shape[1]
    writer.writerow([n,m])
    for i in range(n):
        for j in range(m):
            value = X[i,j]
            if value > 0:
                writer.writerow([i,j,value])
    fp.close()

def load_coo(filename, verbose=False):
    fp = open(filename, 'r')
    reader = csv.reader(fp, delimiter=',')
    header = reader.next()
    if len(header) != 2:
        raise Exception("Wrong csv header format")
    
    n = int(header[0])
    m = int(header[1])
    X = np.zeros((n,m), dtype=np.float32)
    it = 0
    t0 = time.time()
    for line in reader:
        if verbose == True:
            t1 = time.time()
            if t1 - t0 > 10:
                print "Progress: %.2fM lines processed" % (float(it) / 1000000)
            t0 = t1
        i = int(line[0])
        j = int(line[1])
        value = float(line[2])
        if value < 0:
            print 'Warning: setting negative value to zero, position (%d,%d)' % (i,j)
            value = 0.0
        X[i,j] = value
        it += 1
    
    fp.close()
    return X

def load_coo_sparse(filename, verbose=False):
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
    
    if verbose == True:
        print 'Number of rows', N, n
        print 'Number of columns', M, m
    
    n, m = N, M
    
    t0 = time.time()
    if verbose == True:
        print 'Read in: ', t0-tz
    data = np.array(vals, dtype=np.float32)
    X = csr_matrix((vals,(rows,cols)),shape=(n, m),dtype=np.float32)
    return X

def write_dense_csv(filename, X, delimiter=','):
    fp = open(filename, 'w')
    writer = csv.writer(fp, delimiter=delimiter)
    for i in range(X.shape[0]):
        writer.writerow(X[i,:])
    fp.close()
