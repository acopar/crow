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

from crow.utils import *
from crow.preprocess import factors, procdata, blockmap
from crow.core import finalize, factorize

def nice_print(params):
    fact_rank = 'k1xk2 = %sx%s' % (params['k1'], params['k2']) 
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
    parser = argparse.ArgumentParser(description='Crow')
    parser.add_argument("-a", "--arguments", default='', help='Pass arguments in key=value pairs separated with commas (deprecated, use -k1 and -k2 instead)')
    parser.add_argument("-b", "--blocks", help="Block configuration (default 1x1)", default='1x1')
    parser.add_argument("-d", "--double", help='Double precision', action="store_true")
    parser.add_argument("-e", "--error", help="Print error function", action="store_true")
    parser.add_argument("-f", "--force", help='Force all steps. Overwrite files during execution.', action="store_true")
    parser.add_argument("-g", "--gpu", help="Run on GPU", action="store_true")
    parser.add_argument("-i", "--max-iter", type=int, default=10, help='Number of iterations (default 10)')
    parser.add_argument("-k1", "--k1", default=None, help='First rank value (default 10)')
    parser.add_argument("-k2", "--k2", default=None, help='Second rank value (default 10)')
    
    parser.add_argument("-m", "--imbalanced", help="Imbalanced partitioning", action="store_true")
    parser.add_argument("-n", "--init", help="Initialization (default random)", default='random')
    parser.add_argument("-o", "--orthogonal", help='Run with orthogonal constraints', action="store_true")
    
    parser.add_argument("-M", "--method", help='Override method selection', default='')
    parser.add_argument("-S", "--seed", help='Override seed', type=int, default=42)
    
    # do not specify unless different from blocks
    parser.add_argument("-p", "--parallel", type=int, default=None, help='Parallelization degree (default: number of blocks)')
    parser.add_argument("-s", "--sparse", help="Run sparse", action="store_true")
    parser.add_argument("-t", "--stop", help='Stopping criteria', default='')
    
    parser.add_argument('--data-dir', default='data/', help='specify data directory')
    parser.add_argument('--cache-dir', default='cache/', help='specify cache directory')
    parser.add_argument('--results-dir', default='results/', help='specify results directory')
    
    # Debugging flags
    parser.add_argument("-V", "--Verbose", help='Verbosity', action="store_true")
    parser.add_argument("--no-transfer", help="No data transfer (benchmark only)", action="store_true")
    
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
        ext = os.path.splitext(data_file)[1]
        exts = ['.npz', '.coo', '']
        if ext != '':
            exts = [ext]
        
        for ext in exts:
            data_base = '%s%s' % (os.path.basename(data_file), ext)
            data_file2 = to_path(args.data_dir, data_base)
            if os.path.isfile(data_file2):
                data_file = data_file2
                break
    
    if not os.path.isfile(data_file):
        raise Exception("File not found: %s" % data_file)
    
    context = 'cpu'
    if args.gpu == True:
        context = 'gpu'
    
    rulefile = 'nmtf_long'
    if args.orthogonal:
        rulefile = 'nmtf_ding'
    
    if args.method:
        rulefile = args.method
    
    k1 = None
    k2 = None
    if args.k1 != None:
        k1 = args.k1
        if args.k2 != None:
            k2 = args.k2
        else:
            k2 = args.k1
    elif args.k2 != None:
        k2 = args.k2
        k1 = args.k2
    else:
        k1 = 10
        k2 = 10
    
    arguments = args.arguments
    if arguments == '':
        arguments = 'k=%s,l=%s' % (k1, k2)
    
    sync = True
    if args.no_transfer:
        sync = False
    data_label = os.path.splitext(os.path.basename(data_file))[0]
    
    ensure_dir_exact(args.results_dir)
    
    params = {'context': context, 'sparse': args.sparse, 'blocks': blocks, 'k1': k1, 'k2': k2,
        'arguments': arguments, 
        'parallel': parallel, 'error': args.error, 'max_iter': args.max_iter, 'rulefile': rulefile, 
        'init': args.init, 'imbalanced': args.imbalanced, 'sync': sync, 'seed': args.seed,
        'verbose': args.Verbose, 'force': args.force, 'double': args.double,
        'cache_folder': args.cache_dir, 'results_folder': args.results_dir,
        'output_folder': to_path(args.results_dir, 'history'),
        'data_file': data_file, 'stop': args.stop}
    
    run_wrapper(params)


def run_wrapper(params, merge=True):
    CACHE = params['cache_folder']
    RESULTS = params['results_folder']
    
    factor_cache = to_path(CACHE, 'factors')
    blockmap_file = to_path(CACHE, 'index', 'index.pkl')
    
    if 'data_file' not in params:
        raise Exception("Please provide a path to a data file")
    data_file = params['data_file']
    cache_folder = to_path(CACHE, 'data')
    data_folder = get_cache_folder(data_file, cache_folder)
    
    factor_folder = to_path(RESULTS)
    output_folder = to_path(CACHE, 'storage') # gets overriden
    results_folder = params['results_folder']
    
    template = {'blocks': (1,1), 'sparse': False, 'max_iter': 100, 'context': 'cpu', 'sync': True, 'k1': 10, 'k2': 10,
        'arguments': 'k=10,l=10', 'parallel': 1, 'rulefile': 'nmtf_long', 'init': 'random', 'seed': 42,
        'multiplier': 1, 'error': True, 'override': False, 'debug': None, 'test': False, 'imbalanced': False,
        'data_folder': data_folder, 'data_file': data_file, 'factor_folder': factor_folder, 
        'results_folder': results_folder, 'output_folder': output_folder, 'factor_cache': factor_cache,
        'blockmap_file': blockmap_file, 'stop': '', 'double': False,
    }
    
    params = from_template(template, params)
    
    data_cache_module(params)
    factor_init_module(params)
    blockmap_init_module(params)
    sys.stdout.flush()
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
    sync = params['sync']
    
    if context == 'epu':
        context = 'cpu'
        sync = False
        
    if context == 'hpu':
        context = 'gpu'
        sync = False
    
    imbalanced = False
    if params['imbalanced']:
        if params['parallel'] > 1 and params['sparse']:
            imbalanced = True
    
    d = {'nb': nb, 'mb': mb, 'max_iter': params['max_iter'], 'seed': params['seed'], 'double': params['double'],
        'sparse': params['sparse'], 'imbalanced': imbalanced, 'init': params['init'], 'cache_folder': params['cache_folder'],
        'parallel': params['parallel'], 'context': context, 'multiplier': params['multiplier']}
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
    if config['imbalanced']:
        balanced = False
    
    data_folder = procdata.dataset_to_blocks(data_file, cache_folder, blocks=[(nb,mb)], sparse=params['sparse'], balanced=balanced)
    
    return data_folder

def factor_init_module(params):
    # Generates factors
    # Partitions factors
    # factor_folder -> factor_cache
    dimensions = {'k': int(params['k1']), 'l': int(params['k2'])}
    cache_folder = params['data_folder']
    factor_folder = params['factor_folder']
    factor_cache = params['factor_cache']
    results_folder = params['results_folder']
    
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
    factors.prepare_results(results_folder, matrices)


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
    
    dimensions = {'k': int(params['k1']), 'l': int(params['k2'])}
    config = get_config(params)
    
    output_folder = params['output_folder']
    atexit.register(MPI.Finalize)
    comm = MPI.COMM_WORLD
    output = None
    if output_folder:
        output = to_path(output_folder, '%d_%d.pkl' % (dimensions['k'], dimensions['l']))
    
    data_folder = params['data_folder']
    results_folder = params['results_folder']
    factor_cache = params['factor_cache']
    
    rulefile = params['rulefile']
    
    inputs = {'data': data_folder, 'method': rulefile, 'factors': factor_cache, 
        'index': params['blockmap_file']}
    outputs = {'output': output, 'results': results_folder}

    dense = not params['sparse']
    sync = params['sync']
    
    flags = {'dense': dense, 'error': params['error'], 'test': params['test'], 
        'override': params['override'], 'debug': params['debug'], 'sync': params['sync'],
        'stop': params['stop'], 'double': params['double']
    }
    
    dimensions = {}
    data = factorize.run(inputs, outputs, config, dimensions, flags=flags)
    if not data:
        return
    if comm.rank == 0:
        print 'Average iteration time:', data['itertime']



    

if __name__ == "__main__":
    main()