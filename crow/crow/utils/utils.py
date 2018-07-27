#!/usr/bin/env python

import os
import cPickle
import time
import csv
import numpy as np
from scipy.sparse import csr_matrix

def ensure_dir(f):
    d = os.path.dirname(f)
    if d:
        if not os.path.exists(d):
            try:
                os.makedirs(d)
            except OSError, e:
                print f
                raise e

def ensure_dir_exact(d):
    d = os.path.join(d, '')
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except OSError, e:
            print d
            raise e

def remove(d):
    if os.path.isfile(d):
        os.remove(d)
    if os.path.isdir(d):
        os.rmdir(d)

def load_file(filename):
    # load pickle file
    if os.path.isfile(filename) == False:
        print "Error: Cannot open file: %s" % filename
        return None
    fp = open(filename, 'rb')
    d = cPickle.load(fp)
    fp.close()
    return d

def dump_file(filename, data):
    # dump pickle file
    ensure_dir(filename)
    fp = open(filename, 'wb')
    cPickle.dump(data, fp, 2)
    fp.close()

def load_numpy(filename):
    if os.path.isfile(filename) == False:
        print "Error: Cannot open file: %s" % filename
        return None
    d = np.load(filename)
    if 'indices' in d:
        # sparse
        X = csr_matrix((d['data'], d['indices'], d['indptr']), shape=d['shape'])
        return X
    elif 'data' in d:
        return d['data']
    else:
        print "Error: No numpy data in file %s" % filename
        return None

def save_numpy(filename, data):
    ensure_dir(filename)
    if type(data) == csr_matrix:
        np.savez(filename, data=data.data, indices=data.indices, indptr=data.indptr, shape=data.shape)
    else:
        np.savez(filename, data=data)

def file_concat(parts):
    path = ''
    for i in range(len(parts)):
        path = os.path.join(path, parts[i])
    return path

def to_path(*parts):
    return file_concat(parts)

def check_file(f, soft=False):
    if not os.path.isfile(f):
        if soft == True:
            return False
        else:
            raise Exception("File not found %s" % f)
    return True

class Timer():
    def __init__(self, system=True):
        self.t = {}
        self.c = {}
        self.last = None
        self.system = system
    
    def time(self):
        if self.system == False:
            return time.time()
        else:
            return os.times()[4]
    
    def get(self, label=None):
        if label not in self.t:
            return None
        else:
            return self.t[label]
    
    def check(self, label=None):
        if label not in self.t or self.t[label] == None:
            self.t[label] = 0.0
    
    def labelize(self, label):
        if label == None:
            if self.last:
                label = self.last
        return label
    
    def clear(self):
        self.t = {}
        self.c = {}
        self.last = None
    
    def reset(self, label=None):
        label = self.labelize(label)
        self.t[label] = 0.0
        self.c[label] = self.time()
    
    def start(self, label=None):
        label = self.labelize(label)
        if label == None:
            return
        self.check(label=label)
        self.c[label] = self.time()
        self.last = label
    
    def pause(self, label=None):
        label = self.labelize(label)
        if label == None:
            return
        if label in self.c or self.c[label] != None:
            self.t[label] += self.time() - self.c[label]
    
    def stop(self, label=None):
        self.pause(label=label)
        if self.last:
            self.last = None
    
    def split(self, label=None):
        label = self.labelize(label)
        if label == None or label == self.last:
            return
        if self.last:
            self.stop(label=self.last)
        self.start(label=label)
        
    def __str__(self):
        elements = sorted(self.t.items(), key=lambda x: x[1], reverse=True)
        total = sum([t[1] for t in elements])
        portions = [(key, value/total) for key, value in elements]
        portions = [(key, '%.3f' % value) for key, value in portions]
        return str(portions)

    def add(self, other):
        for key in other.t:
            if key in self.t:
                self.t[key] = self.t[key] + other.t[key]
            else:
                self.t[key] = other.t[key]
    
    def asdict(self):
        elements = sorted(self.t.items(), key=lambda x: x[1], reverse=True)
        total = sum([t[1] for t in elements])
        portions = [(key, value/total) for key, value in elements]
        portions = {key: value for key, value in portions}
        return portions

    def elapsed(self):
        return self.t
    
    def total_elapsed(self):
        elements = sorted(self.t.items(), key=lambda x: x[1], reverse=True)
        total = sum([t[1] for t in elements])
        return total
        
        
def load_csv_dict(filename, delimiter=','):
    # loads csv file into array of rows (arrays)
    ensure_dir(filename)
    if not os.path.isfile(filename):
        print "Error: Cannot open file: %s" % filename
        return None
    
    fp = open(filename)
    
    reader = csv.reader(fp, delimiter=delimiter)
    try:
        attributes = reader.next()
    except StopIteration:
        fp.close()
        return None
    data = []
    try:
        for row in reader:
            data.append({a:row[i] for i,a in enumerate(attributes)})
    except Exception, e:
        print traceback.format_exc()
        print "Filename", filename
        return None
    fp.close()
    return data

def save_csv_dict(filename, data, columns=None, append=False):
    # write csv file (dict)
    ensure_dir(filename)
    new_file = False
    if not os.path.isfile(filename):
        new_file = True
    
    if append:
        fp = open(filename, 'a')
    else:
        fp = open(filename, 'w')
    if not fp:
        print "Error: Cannot open file: %s" % filename
        return None
    
    writer = csv.writer(fp, delimiter=',')
    attributes = None
    if columns != None:
        attributes = columns
    else:
        if len(data) == 0:
            print "Error: write_csv_dict: no data to write"
            return None
        attributes = sorted(data[0].keys())
    if append == False or new_file:
        writer.writerow([a for a in attributes])
    
    for line in data:
        writer.writerow([line[a] if a in line else '' for a in attributes])
    fp.close()

def from_template(x, y):
    dct = {key: value for key, value in x.items()}
    for key in y:
        dct[key] = y[key]
    return dct

def isfloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False