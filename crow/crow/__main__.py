#!/usr/bin/env python

import sys
import os
import time
import traceback
import subprocess
import argparse
import simplejson as json

from mpi4py import MPI
import atexit

from crow.config import *
from crow.utils import *
from crow.preprocess import factors, procdata, blockmap
from crow.core import finalize, factorize

def nice_print(params):
    dimensions = from_arguments(params['arguments'])
    fact_rank = 'k1xk2 = %sx%s' % (dimensions['k'], dimensions['l']) 
    method_name = '%s' % params['rulefile']
    if method_name == 'nmtf_long':
        method_name = 'Non-orthogonal NMTF (nmtf_long)'
    if method_name == 'nmtf_ding':
        method_name = 'Orthogonal NMTF (nmtf_ding)'
    
    print 'Data: %s\nParameters: %s\nMethod: %s\nMax iterations: %d' % (params['data_file'], fact_rank, method_name, params['max_iter'])
    print 'Parallelization: %dx%s, partitions: %dx%d' % (params['parallel'], params['context'], params['blocks'][0], params['blocks'][1])

def mpiexec(rank, params):
    environ = os.environ
    
    environ['OMP_NUM_THREADS'] = '1'
    nice_print(params)
    
    proc = subprocess.Popen(['mpirun', '--allow-run-as-root', '-c', str(rank), 'crow-runner', json.dumps(params)], 
        env=environ)
    
    out, err = proc.communicate()
    return out, err


def main():
    parser = argparse.ArgumentParser(version=VERSION, description='Crow')
    parser.add_argument("-a", "--arguments", default='', help='Pass arguments in key=value pairs separated with commas (deprecated, use -k1 and -k2 instead)')
    parser.add_argument("-b", "--blocks", help="Block configuration (default 1x1)", default='1x1')
    parser.add_argument("-e", "--error", help="Print error function", action="store_true")
    parser.add_argument("-f", "--force", help='Force all steps. Overwrite files during execution.', action="store_true")
    parser.add_argument("-g", "--gpu", help="Run on GPU", action="store_true")
    parser.add_argument("-i", "--max-iter", type=int, default=10, help='Number of iterations (default 10)')
    parser.add_argument("-k1", "--k1", default=None, help='First rank value (default 10)')
    parser.add_argument("-k2", "--k2", default=None, help='Second rank value (default 10)')
    
    parser.add_argument("-m", "--imbalanced", help="Imbalanced partitioning", action="store_true")
    parser.add_argument("-n", "--init", help="Initialization (default random)", default='random')
    parser.add_argument("-o", "--orthogonal", help='Run with orthogonal constraints', action="store_true")
    # do not specify unless different from blocks
    parser.add_argument("-p", "--parallel", type=int, default=None, help='Parallelization degree (default: number of blocks)')
    parser.add_argument("-s", "--sparse", help="Run sparse", action="store_true")
    parser.add_argument("-t", "--stop", help='Stopping criteria', default='')
    
    # Debugging flags
    parser.add_argument("-V", "--Verbose", help='Verbosity', action="store_true")
    
    parser.add_argument('args', nargs=1, help='Other args')
    args = parser.parse_args()
    
    blocks = parse_block(args.blocks)
    
    rank = blocks[0] * blocks[1]
    parallel = rank
    if args.parallel:
        rank = args.parallel
        parallel = args.parallel
    
    data_file = args.args[0]
    if not os.path.isfile(data_file):
        data_base = os.path.basename(data_file)
        data_file2 = to_path(DATA, data_base)
        if not os.path.isfile(data_file2):
            raise Exception("File not found: %s" % data_file)
        data_file = data_file2
        
    context = 'cpu'
    if args.gpu == True:
        context = 'gpu'
    
    rulefile = 'nmtf_long'
    if args.orthogonal:
        rulefile = 'nmtf_ding'
    
    arguments = args.arguments
    if arguments == '':
        if args.k1 != None:
            arguments = 'k=%s' % args.k1
            if args.k2 != None:
                arguments = '%s,l=%s' % (arguments, args.k2)
            else:
                arguments = '%s,l=%s' % (arguments, args.k1)
        elif args.k2 != None:
            arguments = 'k=%s,l=%s' % (args.k2, args.k2)
        else:
            arguments = 'k=10,l=10'
    
    params = {'context': context, 'sparse': args.sparse, 'blocks': blocks, 'arguments': arguments, 
        'parallel': parallel, 'error': args.error, 'max_iter': args.max_iter, 'rulefile': rulefile, 
        'init': args.init, 'unbalanced': args.imbalanced, 'verbose': args.Verbose, 'force': args.force,
        'data_file': data_file, 'stop': args.stop}
    
    run_wrapper(params)


def run_wrapper(params, merge=True):
    factor_cache = to_path(CACHE, 'factors')
    blockmap_file = to_path(CACHE, 'index', 'index.pkl')
    
    if 'data_file' not in params:
        raise Exception("Please provide a path to a data file")
    data_file = params['data_file']
    cache_folder = to_path(CACHE, 'data')
    data_folder = get_cache_folder(data_file, cache_folder)
    
    factor_folder = to_path(RESULTS, 'factors')
    output_folder = to_path(STORAGE, 'latest')
    results_folder = to_path(output_folder, 'storage')
    
    template = {'blocks': (1,1), 'sparse': False, 'max_iter': 100, 'context': 'cpu', 'sync': True,
        'arguments': 'k=20,l=20', 'parallel': 1, 'rulefile': 'nmtf_long', 'init': 'random', 
        'multiplier': 1, 'error': True, 'override': False, 'debug': None, 'test': False, 'unbalanced': False,
        'data_folder': data_folder, 'data_file': data_file, 'factor_folder': factor_folder, 
        'results_folder': results_folder, 'output_folder': output_folder, 'factor_cache': factor_cache,
        'blockmap_file': blockmap_file, 'stop': ''
    }
    
    params = from_template(template, params)
    
    data_cache_module(params)
    factor_init_module(params)
    blockmap_init_module(params)
    out, err = mpiexec(params['parallel'], params)
    if merge:
        finalize.merge_and_test(params)
        print 'Factors U.npz, S.npz, V.npz are stored in %s' % RESULTS
        print 'Convert them to csv like this:'
        print '    $ crow-conv results/S.npz results/S.csv'
        print

def get_config(params):
    nb, mb = params['blocks']
    
    context = params['context']
    sync = True
    
    if context == 'epu':
        context = 'cpu'
        sync = False
        
    if context == 'hpu':
        context = 'gpu'
        sync = False
    
    unbalanced = False
    if params['unbalanced']:
        if params['parallel'] > 1 and params['sparse']:
            unbalanced = True
    
    d = {'nb': nb, 'mb': mb, 'max_iter': params['max_iter'], 'seed': 0, 
        'unbalanced': unbalanced, 'init': params['init'], 'parallel': params['parallel'], 
        'context': context, 'multiplier': params['multiplier']}
    return d

def data_cache_module(params):
    # Reads csv and splits data into blocks
    # Blocks are cached
    # data_file -> cache_folder
    nb, mb = params['blocks']
    
    data_file = params['data_file']
    cache_folder = params['data_folder']
    
    config = get_config(params)
    
    balanced = True
    if config['unbalanced']:
        balanced = False
    
    data_folder = procdata.dataset_to_blocks(data_file, cache_folder, blocks=[(nb,mb)], sparse=params['sparse'], balanced=balanced)
    
    return data_folder

def factor_init_module(params):
    # Generates factors
    # Partitions factors
    # factor_folder -> factor_cache
    dimensions = from_arguments(params['arguments'])
    cache_folder = params['data_folder']
    factor_folder = params['factor_folder']
    factor_cache = params['factor_cache']
    config = get_config(params)
    
    dense = not params['sparse']
    flags = {'dense': dense, 'error': params['error'], 'test': params['test'], 
        'override': params['override'], 'debug': params['debug']}
    
    output = params['output_folder']
    if output != None:
        ensure_dir_exact(output)

    matrices = [{'type': 'data', 'name': 'X', 'size': 'nm'}, 
        {'type': 'factor', 'name': 'U', 'size': 'nk'}, 
        {'type': 'factor', 'name': 'V', 'size': 'ml'}, 
        {'type': 'factor', 'name': 'S', 'size': 'kl'}, 
        {'type': 'error', 'name': 'E', 'size': '11'}]
    
    X = factors.data_analyze(cache_folder, factor_folder, config, dimensions, matrices)
    factors.generate_factors(factor_folder, config, dimensions, matrices, X)
    factors.partition_factors(factor_folder, factor_cache, config, dimensions, matrices)


def blockmap_init_module(params):
    config = get_config(params)
    factor_folder = params['factor_folder']
    idx_file = params['blockmap_file']
    blockmap.generate_blockmap(config, factor_folder, idx_file)    

def run():
    try:
        core()
    except Exception:
        print "ERROR: Exception in process %d:" % MPI.COMM_WORLD.rank
        print traceback.format_exc()


def core():
    args = sys.argv[1:]
    params = json.loads(args[0])
    
    dimensions = from_arguments(params['arguments'])
    config = get_config(params)
    
    output_folder = params['output_folder']
    atexit.register(MPI.Finalize)
    comm = MPI.COMM_WORLD
    output = None
    if output_folder:
        output = to_path(output_folder, '%d.pkl' % comm.rank)
    
    data_folder = params['data_folder']
    results_folder = params['results_folder']
    factor_cache = params['factor_cache']
    
    rulefile = params['rulefile']
    if params['error'] == True:
        if rulefile == 'nmtf_long':
            rulefile = 'nmtf_long_err'
        elif rulefile == 'nmtf_ding':
            rulefile = 'nmtf_ding_err'
    
    inputs = {'data': data_folder, 'method': rulefile, 'factors': factor_cache, 
        'index': params['blockmap_file']}
    outputs = {'output': output, 'results': results_folder}

    dense = not params['sparse']
    sync = params['sync']
    
    flags = {'dense': dense, 'error': params['error'], 'test': params['test'], 
        'override': params['override'], 'debug': params['debug'], 'sync': params['sync'],
        'stop': params['stop']
    }
    
    dimensions = {}
    data = factorize.run(inputs, outputs, config, dimensions, flags=flags)
    if not data:
        return
    if comm.rank == 0:
        print 'Average iteration time:', data['itertime']



    

if __name__ == "__main__":
    main()