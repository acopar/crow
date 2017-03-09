#!/usr/bin/env python

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

def write_csv(filename, X):
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

def read_csv(filename, verbose=False):
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
        X[i,j] = r
        it += 1
    
    fp.close()
    return X


def main():
    parser = argparse.ArgumentParser(version=VERSION, description='Crow')
    parser.add_argument("-d", "--delimiter", default="comma", help="Change delimiter")
    parser.add_argument("--header", help="Skip csv header line")
    
    parser.add_argument('args', nargs='2', help='Two filenames in order: input output')
    args = parser.parse_args()
    
    argv = args.args
    src = argv[0]
    dst = argv[1]
    X = load_csv(src)
    if not X is None:
        X = np.array(X, dtype=np.float32)
        write_csv(dst, X)
    else:
        raise Exception("Problem with opening csv file %s" % src)


if __name__ == "__main__":
    main()