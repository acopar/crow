#!/usr/bin/env python

import sys
import os
import time
import traceback
import subprocess
import argparse

from crow.config import *
from crow.utils import *
from crow.__main__ import run_wrapper


def get_output_indexed(dataset, rulefile, idx, blocks):
    data_file = dataset[0]
    databasename = os.path.basename(data_file)
    data_base = os.path.splitext(databasename)[0]
    rulename = os.path.basename(rulefile)
    rulename = os.path.splitext(rulename)[0]
    output = to_path(RESULTS, data_base, '%d' % idx, '%d_%d' % (blocks[0], blocks[1]))
    return output

def cmp_profile(dct, dct2):
    equal = True
    for key in dct:
        if key in ['ID', 'timestamp']:
            continue
        if str(dct[key]) != str(dct2[key]):
            equal = False
            break
    
    return equal

def run_setups(dataset, method, setups, k = (20,20), max_iter=100, init='random', save=True, multiplier=1, sync=True, sparse=True):
    init_label = init
    if init not in ['random', 'vcol']:
        init = 'ignore'
    
    data_file = dataset
    cache_folder = to_path(CACHE, 'data')
    data_folder = get_cache_folder(data_file, cache_folder)
    factor_folder = to_path(RESULTS, 'factors')
    results_folder = to_path(STORAGE, 'storage')
    
    a = 'k=%d,l=%d' % (k[0], k[1])
    template = {'blocks': (1,1), 'sparse': sparse, 'max_iter': max_iter, 'context': 'cpu', 'sync': sync,
        'k': k, 'arguments': a, 'parallel': 1, 'rulefile': method, 'init': init, 'multiplier': multiplier,
        'error': True, 'override': False, 'debug': None, 'test': False, 'unbalanced': False,
        'data_folder': data_folder, 'data_file': data_file, 'factor_folder': factor_folder, 
        'results_folder': results_folder, 'output_folder': None,
        'args': [data_file]}
    
    for se in setups:
        se = from_template(template, se)
        blocks = se['blocks']
        context = se['context']
        if sync == False:
            if context == 'cpu':
                context = 'epu'
            if context == 'gpu':
                context = 'hpu'
        if save == True:
            dataname = os.path.splitext(os.path.basename(data_file))[0]
            index_file = to_path(RESULTS, 'result_idx', '%s.csv' % dataname)
            columns = ['ID','method','init','context','parallel','blocks','k',
                'max_iter','multiplier','sparse','unbalanced','sync','timestamp']
            
            dct = {'ID': 0, 'method': method, 'init': init_label, 'context': context, 'timestamp': int(time.time())}
            for col in columns:
                if col not in dct:
                    dct[col] = se[col]
            
            data = load_csv_dict(index_file)
            data2 = []
            
            counter = 0
            replace = False
            if not data is None:
                for d in data:
                    if cmp_profile(dct, d):
                        replace = True
                        counter = int(d['ID'])
                        dct['ID'] = counter
                        data2.append(dct)
                    else:
                        data2.append(d)
                
                if not replace:
                    print 'not replace'
                    for d in data:
                        dix = int(d['ID'])
                        if dix >= counter:
                            counter = dix+1
                        #data2.append(d)
                    dct['ID'] = counter
                    data2.append(dct)
            else:
                data2.append(dct)
            save_csv_dict(index_file, data2, columns=columns)
            
            output_folder = get_output_indexed(dataset, method, counter, blocks)
            se['output_folder'] = output_folder
        
        run_wrapper(se)

def dataname_to_path(dataname):
    return to_path(DATA, dataname, '%s.csv' % dataname)

def random_sparse(n, m, density=1.0):
    X = np.zeros((n,m), dtype=np.float32, order='C')
    for i in range(n):
        for j in range(m):
            rnd = np.random.random()
            if rnd < density:
                r = np.random.random()
                X[i,j] = r
    
    return X

def basic_test():
    cache_folder = get_cache_folder('../data/test.coo', to_path(CACHE, 'data'))
    npzfile = to_path(cache_folder, '1_1', '0_0.npz')
    X = random_sparse(100, 100)
    save_numpy(npzfile, X)
    
    dataset = 'test'
    setups = [{'blocks': (1,1), 'parallel': 1, 'context': 'cpu'}]
    run_setups(dataset, 'nmtf_long', setups, sparse=False)
    
def speedup_test():
    cache_folder = get_cache_folder('../data/test.coo', to_path(CACHE, 'data'))
    npzfile = to_path(cache_folder, '1_1', '0_0.npz')
    X = random_sparse(10000, 1000, density=1.0)
    save_numpy(npzfile, X)
    
    dataset = 'test'
    setups = [{'blocks': (1,1), 'parallel': 1, 'context': 'cpu'}]
    run_setups(dataset, 'nmtf_long', setups, sparse=False)

    setups = [{'blocks': (4,2), 'parallel': 8, 'context': 'cpu'}]
    run_setups(dataset, 'nmtf_long', setups, sparse=False)
    
    setups = [{'blocks': (1,1), 'parallel': 1, 'context': 'gpu'}]
    run_setups(dataset, 'nmtf_long', setups, sparse=False)
    
    setups = [{'blocks': (2,2), 'parallel': 4, 'context': 'gpu'}]
    run_setups(dataset, 'nmtf_long', setups, sparse=False)

def gpu_test():
    cache_folder = get_cache_folder('../data/test.coo', to_path(CACHE, 'data'))
    npzfile = to_path(cache_folder, '1_1', '0_0.npz')
    X = random_sparse(1000, 1000)
    save_numpy(npzfile, X)
    
    dataset = 'test'
    setups = [{'blocks': (1,1), 'parallel': 1, 'context': 'gpu'}]
    run_setups(dataset, 'nmtf_long', setups, sparse=False)

    setups = [{'blocks': (2,2), 'parallel': 4, 'context': 'gpu'}]
    run_setups(dataset, 'nmtf_long', setups, sparse=False)

def main():
    parser = argparse.ArgumentParser(version=VERSION, description='Crow')
    parser.add_argument("-b", "--benchmark", help="Benchmark CPU and GPU speed", action="store_true")
    parser.add_argument("-s", "--speedup", help="Benchmark CPU and GPU speed", action="store_true")
    parser.add_argument("-g", "--gpu", help="Multi-GPU test", action="store_true")

    parser.add_argument('args', nargs='*', help='Other args')
    args = parser.parse_args()
    
    argv = args.args
    if args.benchmark:
        benchmark(argv)
    elif args.gpu:
        gpu_test()
    elif args.speedup:
        speedup_test()
    else:
        basic_test()

    
if __name__ == "__main__":
    main()
