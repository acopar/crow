import os
import numpy as np
from crow.utils import *
from crow.convert.csv import *

def merge_and_test(params):
    factor_folder = params['factor_folder']
    rulefile = params['rulefile']
    results_folder = params['results_folder']
    block_config = params['blocks']
    
    matrices = [{'type': 'data', 'name': 'X', 'size': 'nm'}, {'type': 'factor', 'name': 'U', 'size': 'nk'}, 
        {'type': 'factor', 'name': 'V', 'size': 'ml'}, {'type': 'factor', 'name': 'S', 'size': 'kl'}, 
        {'type': 'error', 'name': 'E', 'size': '11'}]
    
    sizes = {}
    for p in matrices:
        key = p['name']
        size = p['size']
        sizes[key] = size
    
    nb = block_config[0]
    mb = block_config[1]
    
    ffile = to_path(factor_folder, 'factors.pkl')
    sfile = to_path(factor_folder, 'slices.pkl')
    dimensions, storage = load_file(ffile)
    slices, block_mask = load_file(sfile)
    
    matrix_list = []
    for p in matrices:
        if p['type'] != 'data':
            matrix_list.append(p['name'])
    
    storage = {}
    for key in matrix_list:
        storage_folder = to_path(results_folder, key)
        storage[key] = {}
        for bid in block_mask.keys():
            storage_out = to_path(storage_folder, '%d_%d.pkl' % (bid[0], bid[1]))
            storage[key][bid] = load_file(storage_out)
    
    new_factors = {}
    for key in storage:
        size = sizes[key].replace('l', 'k')
        
        X = None
        if size == 'nk':
            sorted_factor = [storage[key][(i,0)] for i in range(nb)]
            X = np.vstack(sorted_factor)
        
        if size == 'mk':
            sorted_factor = [storage[key][(0,i)] for i in range(mb)]
            X = np.vstack(sorted_factor)
        
        if size in ['kk', '11']:
            X = storage[key][(0,0)]
        
        if X is None:
            print 'Error loading %s' % key
        new_factors[key] = X
    
    dump_file(ffile, (dimensions, new_factors))
    factordict_to_npz(ffile, factor_folder)
    measure_error(params)


def factordict_to_npz(filename, factor_folder):
    dimensions, new_factors = load_file(filename)
    for key in new_factors:
        factor = new_factors[key]
        filename = to_path(factor_folder, '%s.npz' % key)
        save_numpy(filename, factor)

def measure_error(params):
    cache_folder = params['data_folder']
    factor_folder = params['factor_folder']
    
    ffile = to_path(factor_folder, 'factors.pkl')
    dimensions, storage = load_file(ffile)
    
    U = storage['U']
    S = storage['S']
    V = storage['V']
    E = storage['E']
    err = E.sum()
    if err != 0.0:
        print 'Error function:', err

    