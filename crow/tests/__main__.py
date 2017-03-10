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

def benchmark(argv):
    sparse_map = {'ArrayExpress': False, 'TCGA-BRCA': False, 'fetus': True,
        'retina-dense': False, 'cochlea-dense': False, 'retina': True, 'cochlea': True}
    data_list = ['ArrayExpress', 'TCGA-BRCA', 'fetus', 'retina-dense', 'cochlea-dense']
    data_list = ['ArrayExpress']
    datasets = [(dataname_to_path(key), sparse_map[key]) for key in data_list]

    method_list = ['nmtf_long']
    update_rules = [(m, 'random') for m in method_list]
    
    block_map = {
        'ArrayExpress': 'v',
        'retina-dense': 'r',
        'cochlea-dense': 'r',
        'TCGA-BRCA': 'h',
        'fetus': 'r'
    }
    
    context = 'cpu'
    u = False
    setups = [{'blocks': (1,1), 'parallel': 1, 'context': context, 'unbalanced': u},
            {'blocks': (2,1), 'parallel': 2, 'context': context, 'unbalanced': u},
            {'blocks': (1,2), 'parallel': 2, 'context': context, 'unbalanced': u},
            {'blocks': (4,1), 'parallel': 4, 'context': context, 'unbalanced': u},
            {'blocks': (2,2), 'parallel': 4, 'context': context, 'unbalanced': u},
            {'blocks': (1,4), 'parallel': 4, 'context': context, 'unbalanced': u}]
    #setups = [{'blocks': (2,2), 'parallel': 4, 'context': context, 'unbalanced': u}]
    
    setups = [{'blocks': (3,2), 'parallel': 6, 'context': context}]
    #setups = [{'blocks': (1,1), 'parallel': 1, 'context': context}]

    k_list = [20]
    for dataset in datasets:
        for item in update_rules:
            method = item[0]
            sparse_support = method[1]
            init = item[1]
            if dataset[1] == True and sparse_support == False:
                print 'Skipping sparse dataset %s with rules %s' % (dataset[0], rulefile)
                continue
            
            for k1 in k_list:
                k = (k1, k1)
                run_setups(dataset[0], method, setups, k=k, max_iter=10, init=init, sync=True, sparse=dataset[1])

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

def main():
    parser = argparse.ArgumentParser(version=VERSION, description='Crow')
    parser.add_argument("-b", "--benchmark", help="Benchmark CPU and GPU speed", action="store_true")

    parser.add_argument('args', nargs='*', help='Other args')
    args = parser.parse_args()
    
    argv = args.args
    if args.benchmark:
        benchmark(argv)
    else:
        basic_test()
    
    
if __name__ == "__main__":
    main()
