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

DATASETS = {
     'ArrayExpress': ('ArrayExpress/ArrayExpress.csv', False), 
     'ml-100k': ('movielens/ml-100k/ml-100k.csv', True),
     'ml-1m': ('movielens/ml-1m/ml-1m.csv', True),
     'ml-10m': ('movielens/ml-10m/ml-10m.csv', True), 
     'ml-20m': ('movielens/ml-20m/ml-20m.csv', True),
     'netflix': ('netflix/netflix.csv', True),
     'sparse-1m': ('synthetic/sparse-1m/sparse-1m.csv', True), 
     'dense-1m': ('synthetic/sparse-1m/dense-1m.csv', False),
     'sparse-10m': ('synthetic/sparse-10m/sparse-10m.csv', True), 
     'dense-10m': ('synthetic/sparse-10m/dense-10m.csv', False),
     'sparse-100m': ('synthetic/sparse-100m/sparse-100m.csv', True), 
     'dense-100m': ('synthetic/sparse-100m/dense-100m.csv', False),
     'ESAD-UK': ('ICGC/ESAD-UK/ESAD-UK.csv', True), 
     'LIRI-JP': ('ICGC/LIRI-JP/LIRI-JP.csv', True),
     'fetus': ('giant/fetus/fetus.csv', True), 
     'cochlea': ('giant/cochlea/cochlea.csv', True), 
     'kidney': ('giant/kidney/kidney.csv', True),
     'retina': ('giant/retina/retina.csv', True),
     'TCGA-BRCA': ('TCGA/TCGA-BRCA/TCGA-BRCA.csv', False), 
     'miRNA': ('miRNA/miRNA.csv', False),
     'cochlea-dense': ('giant/cochlea-dense/cochlea-dense.csv', False),
     'retina-dense': ('giant/retina-dense/retina-dense.csv', False),
     'ESAD-UK-dense': ('ICGC/ESAD-UK/ESAD-UK-dense.csv', False),
     'fetus-dense': ('giant/fetus/fetus-dense.csv', False), 
     'kidney-dense': ('giant/kidney/kidney-dense.csv', False),
     'IntAct': ('IntAct/IntAct.csv', True)
}


def load_data_cofigs(data_list):
    return [(to_path(DATA, DATASETS[key][0]), DATASETS[key][1]) for key in data_list]

def get_output(dataset, rulefile, k):
    data_file = dataset[0]
    data_folder = get_data_folder(data_file)
    databasename = os.path.basename(data_file)
    data_base = os.path.splitext(databasename)[0]
    rulename = os.path.basename(rulefile)
    rulename = os.path.splitext(rulename)[0]
    output = to_path(RESULTS, data_base, rulename, 'K%d_%d' % (k[0], k[1]))
    return output

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
    
    data_file, sparse = dataset[0], dataset[1]
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

def benchmark(argv):
    data_list = ['ArrayExpress', 'TCGA-BRCA', 'fetus', 'retina-dense', 'cochlea-dense']
    data_list = ['ArrayExpress']
    datasets = load_data_cofigs(data_list)
    
    method_list = ['nmtf_long_err']
    update_rules = [(m, 'random') for m in method_list]
    
    block_map = {
        'ArrayExpress': 'v',
        'retina-dense': 'r',
        'cochlea-dense': 'r',
        'TCGA-BRCA': 'h',
        'fetus': 'r'
    }
    
    context = 'gpu'
    u = False
    setups = [{'blocks': (1,1), 'parallel': 1, 'context': context, 'unbalanced': u},
            {'blocks': (2,1), 'parallel': 2, 'context': context, 'unbalanced': u},
            {'blocks': (1,2), 'parallel': 2, 'context': context, 'unbalanced': u},
            {'blocks': (4,1), 'parallel': 4, 'context': context, 'unbalanced': u},
            {'blocks': (2,2), 'parallel': 4, 'context': context, 'unbalanced': u},
            {'blocks': (1,4), 'parallel': 4, 'context': context, 'unbalanced': u}]
    #setups = [{'blocks': (2,2), 'parallel': 4, 'context': context, 'unbalanced': u}]
    
    #setups = [{'blocks': (3,2), 'parallel': 6, 'context': context}]
    setups = [{'blocks': (1,1), 'parallel': 1, 'context': context}]

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
                run_setups(dataset, method, setups, k=k, max_iter=10, init=init, sync=True, sparse=dataset[1])


def main():
    parser = argparse.ArgumentParser(version=VERSION, description='Crow')
    parser.add_argument("-b", "--benchmark", help="Benchmark CPU and GPU speed", action="store_true")

    parser.add_argument('args', nargs='*', help='Other args')
    args = parser.parse_args()
    
    argv = args.args
    if args.benchmark:
        benchmark(argv)
    else:
        print "No test selected"
    
    
if __name__ == "__main__":
    main()
