import os
import numpy as np
from crow.utils import *
from crow.convert.csv import *

def merge_and_test(params):
    factor_folder = params['factor_folder']
    rulefile = params['rulefile']
    cache_folder = params['cache_folder']
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
        storage_folder = to_path(cache_folder, 'factors', key)
        storage[key] = {}
        for bid in block_mask.keys():
            storage_out = to_path(storage_folder, '%d_%d.pkl' % (bid[0], bid[1]))
            storage[key][bid] = load_file(storage_out)
            remove(storage_out)
        remove(storage_folder)
    
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
    
    for key in new_factors:
        factor = new_factors[key]
        filename = to_path(factor_folder, '%s.npz' % key)
        save_numpy(filename, factor)
    
    
    ## cleanup
    
    remove(ffile)
    remove(sfile)
    remove(params['blockmap_file'])
    factor_cache = params['factor_cache']
    for i in range(nb):
        for j in range(mb):
            fblock_file = to_path(factor_cache, '%d_%d.pkl' % (i,j))
            remove(fblock_file)
    