#!/usr/bin/env python

import csv
import numpy as np
import time

from crow.utils import *

def generate_synthetic(filename, size=(1000, 1000), density=1.0):
    ensure_dir(filename)
    fp = open(filename, 'w')
    writer = csv.writer(fp, delimiter=',')
    
    n, m = size
    writer.writerow([n,m])
    
    tz = time.time()
    it = 0
    for i in range(n):
        for j in range(m):
            if it > 1 and it % 5000000 == 0:
                print "Progress %dM" % (it / 1000000)
            
            rnd = np.random.random()
            if rnd < density:
                r = np.random.random()
                writer.writerow([i,j,r])
            it += 1
    
    fp.close()
    t0 = time.time()
    print 'Generated in: ', t0-tz

if __name__ == "__main__":
    #generate_synthetic('../../data/synthetic/sparse-1m/sparse-1m.csv', size=(1000, 1000), density=0.01)
    #generate_synthetic('../../data/synthetic/sparse-10m/sparse-10m.csv', size=(10000, 1000), density=0.01)
    generate_synthetic('../../data/synthetic/sparse-100m/sparse-100m.csv', size=(10000, 10000), density=0.01)