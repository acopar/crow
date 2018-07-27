from crow.utils import Timer
from crow.transfer.cputransfer import cpu_reduce
from crow.utils import *

import numpy as np
from scipy.sparse import csr_matrix

import time

def get_dimension(dimensions, n, block):
    if type(dimensions[n]) == type({}):
        return dimensions[n][block]
    else:
        return dimensions[n]

def factorization(f):
    def new_f(*args, **kwargs):
        self = args[0]
        kwargs['X'] = self.storage['X']
        kwargs['U'] = self.storage['U']
        kwargs['S'] = self.storage['S']
        kwargs['V'] = self.storage['V']
        kwargs['E'] = self.storage['E']
        
        blocks_i, blocks_j = self.block_map
        bid = blocks_i[0]
        
        self.operation.bid = bid
        self.operation.dimensions = self.dimensions
        self.operation.blocks = self.block_map[0]
        
        kwargs['n'] = self.dimensions['n']
        kwargs['m'] = self.dimensions['m']
        kwargs['k'] = self.dimensions['k']
        kwargs['l'] = self.dimensions['l']

        self.timer = Timer()
        self.operation.load_kernel()
        self.operation.sync_flag = self.sync
        
        kwargs['print_err'] = self.flags['error']

        h = f(*args, **kwargs)

        self.operation.empty_sync_matrix(None, None, None)
        self.timer.stop()
        
        return h

    return new_f

class Context(object):
    def __init__(self, rank, size, inputs, dimensions, config, flags):
        self.dimensions = dimensions
        self.dense = flags['dense']
        self.test = flags['test']
        self.rank = rank
        self.size = size
        self.sync = flags['sync']
        self.stop = flags['stop']
        self.flags = flags
        self.prev = None
        self.now = None
        self.lazy = False
        self.dtype = np.float32
        if flags['double']:
            self.dtype = np.float64
        
        np.random.seed(42)
        
        self.max_iter = config['max_iter']
        self.balanced = True
        if config['imbalanced']:
            self.balanced = False
        self.timer = Timer()
        self.nb = config['nb']
        self.mb = config['mb']
        self.multiplier = (1, 1)
        
        self.data_folder = to_path(inputs['data'], '%d_%d' % (self.nb, self.mb))
        self.factor_folder = inputs['factors']

        idx_file = inputs['index']
        idx_data = load_file(idx_file)
        block_map, block_map_j, iblock_map, jblock_map, tblock_map = idx_data
        
        self.block_map = block_map[rank]
        self.block_map_j = block_map_j[rank]
        self.block_map = (self.block_map, self.block_map_j)
        
        self.rev_map = {}
        for r in block_map:
            for x in block_map[r]:
                self.rev_map[x] = r
        
        self.iblock_map = iblock_map
        self.jblock_map = jblock_map
        self.tblock_map = tblock_map
        
        self.storage = {}
        self.params = [{'type': 'data', 'name': 'X', 'size': 'nm'}, {'type': 'factor', 'name': 'U', 'size': 'nk'}, 
        {'type': 'factor', 'name': 'V', 'size': 'ml'}, {'type': 'factor', 'name': 'S', 'size': 'kl'}, 
        {'type': 'error', 'name': 'E', 'size': '11'}]
        
        self.number_of_iterations = self.max_iter - 2
        
        if len(self.block_map[0]) > 1 and config['context'] == 'gpu':
            self.lazy = True
            print "Lazy mode activated"
        
        if self.rank == 0:
            cache_folder = config['cache_folder']
            if not cache_folder is None:
                for p in self.params:
                    if p['type'] == 'data':
                        continue
                    key = p['name']
                    storage_folder = to_path(cache_folder, 'factors', key)
                    ensure_dir_exact(storage_folder)
    
    def get_blocks(self):
        return self.block_map[0]

    def super_set_matrix(self, X, bid, key, dim):
        self.storage[key].append(X, Xt=None, key=bid)
        if dim[0] not in self.dimensions:
            self.dimensions[dim[0]] = {}
        self.dimensions[dim[0]][bid] = X.shape[0]
        
        if dim[1] not in self.dimensions:
            self.dimensions[dim[1]] = {}
        self.dimensions[dim[1]][bid] = X.shape[1]
    
    def super_new_matrix(self, bid, key, dim):
        x = get_dimension(self.dimensions, dim[0], bid)
        y = get_dimension(self.dimensions, dim[1], bid)
        
        self.storage[key].append(self.operation.czeros(x,y), key=bid)

    def load(self, data=True):
        data_vars = []
        factor_vars = []
        error_vars = []
        empty_vars = []
        param_vars = []
        
        sizes = {}
        for p in self.params:
            key = p['name']
            size = p['size']
            sizes[key] = size
            if p['type'] == 'data':
                data_vars.append(key)
            elif p['type'] == 'factor':
                factor_vars.append(key)
            elif p['type'] == 'error':
                error_vars.append(key)
            elif p['type'] == 'empty':
                empty_vars.append(key)
            elif p['type'] == 'param':
                param_vars.append(key)
        
        self.data_vars = data_vars
        self.factor_vars = factor_vars
        self.error_vars = error_vars
        self.empty_vars = empty_vars
        self.param_vars = param_vars
        self.dimensions['1'] = 1
        self.models = {}
        
        for key in sizes:
            dim = sizes[key]
            dim = dim.replace('l', 'k')
            if dim in ['nn', 'nm']:
                self.models[key] = 'ij'
            elif dim in 'nk':
                self.models[key] = 'i'
            elif dim == 'mk':
                self.models[key] = 'j'
            else:
                self.models[key] = '0'
            self.models[key] = 'ij'
        
        for idx, jdx in self.block_map[0]:
            bid = (idx, jdx)
            
            if data == True:
                for v in data_vars:
                    filename = to_path(self.data_folder, '%d_%d.npz' % (idx, jdx))
                    if self.dense == False:
                        if self.balanced == True:
                            filename = to_path(self.data_folder, 's%d_%d.npz' % (idx, jdx))
                        else:
                            filename = to_path(self.data_folder, 'i%d_%d.npz' % (idx, jdx))
                    
                    X = self.load_data(filename, self.dense)
                    if self.dtype == np.float64:
                        X = X.astype(np.float64)
                    if self.dtype == np.float32:
                        X = X.astype(np.float32)
                    self.set_matrix(X, bid, v, sizes[v])
            
            factor_file = to_path(self.factor_folder, '%d_%d.pkl' % (idx, jdx))
            factors = load_file(factor_file)
            
            for v in factor_vars:
                self.set_matrix(factors[v], bid, v, sizes[v])
                
            for v in error_vars:
                self.new_matrix(bid, v, sizes[v])

            for v in empty_vars:
                self.new_matrix(bid, v, sizes[v])
            
            for v in param_vars:
                if v not in self.dimensions:
                    raise Exception("Undefined parameter %s" % v)
                p = self.dimensions[v]
                self.number_matrix(bid, v, sizes[v])
                tmp = self.storage[v].get(key=bid)
                self.storage[v].set(tmp + p, key=bid)
    
    
    def load_data(self, filename, dense):
        check_file(filename)
        Xd = load_numpy(filename)
        if dense == True:
            if type(Xd) == np.ndarray:
                X = Xd
            else:
                X = np.array(Xd.todense())
            X[X < 0] = 0.0
        else:
            X = csr_matrix(Xd)
        return X
    
    def save(self, output, cache_folder, data):
        if not output is None and self.rank == 0:
            dump_file(output, data)
        
        output_vars = self.factor_vars + self.error_vars
        if not cache_folder is None:
            for key in output_vars:
                storage_folder = to_path(cache_folder, 'factors', key)
                for bid in self.storage[key].blocks:
                    storage_out = to_path(storage_folder, '%d_%d.pkl' % (bid[0], bid[1]))
                    dump_file(storage_out, self.storage[key].get(key=bid))

    def check_lastN(self, history, EPS, N):
        if len(history) > N:
            last5 = history[-N:]
            condition = False
            for i in range(1,N):
                prev = last5[i-1]
                now = last5[i]
                #print i, prev, now
                
                if EPS * np.abs(now) - np.abs(prev - now) > 0:
                    condition = True
                else:
                    condition = False
                    break
            if condition == True:
                return True
        
    
    def check_stop(self, E=None, history=None):
        if self.stop == None:
            return False
    
        if self.prev == None:
            if E is not None:
                self.prev = E.fetch()[0,0]
            return False
        
        if E is not None:
            self.now = E.fetch()[0,0]
        
        if self.stop == 'e4':
            if np.abs(self.prev - self.now) < 10**(-4):
                return True
        
        if self.stop == 'e5':
            if np.abs(self.prev - self.now) < 10**(-5):
                return True
        
        if self.stop == 'e6':
            if np.abs(self.prev - self.now) < 10**(-6):
                return True
                
        if self.stop == 'e7':
            if np.abs(self.prev - self.now) < 10**(-7):
                return True
        
        if self.stop == 'd3':
            if 10**(-3) * np.abs(self.now) - np.abs(self.prev - self.now) > 0:
                return True
        
        if self.stop == 'd4':
            if 10**(-4) * np.abs(self.now) - np.abs(self.prev - self.now) > 0:
                return True
        
        if self.stop == 'd5':
            if 10**(-5) * np.abs(self.now) - np.abs(self.prev - self.now) > 0:
                return True
        
        if self.stop == 'd6':
            if 10**(-6) * np.abs(self.now) - np.abs(self.prev - self.now) > 0:
                return True
                
        if self.stop == 'd7':
            if 10**(-7) * np.abs(self.now) - np.abs(self.prev - self.now) > 0:
                return True

        if self.stop == 'p5-5':
            if self.check_lastN(history, 10**(-5), 6):
                return True
        
        if self.stop == 'p5-10':
            if self.check_lastN(history, 10**(-5), 11):
                return True
        
        if self.stop == 'p6-5':
            if self.check_lastN(history, 10**(-6), 6):
                return True
        
        if self.stop == 'p6-10':
            if self.check_lastN(history, 10**(-6), 11):
                return True
        
        if self.stop == 'p7-5':
            if self.check_lastN(history, 10**(-7), 6):
                return True
        
        if self.stop == 'p7-10':
            if self.check_lastN(history, 10**(-7), 11):
                return True
        
        self.prev = self.now
        return False
    
    @factorization
    def run_nmtf_long(self, X=None, U=None, S=None, V=None, E=None, n=None, 
        m=None, k=None, l=None, debug=None, print_err=False):
        o = self.operation
        h = []
        
        AA5 = o.zeros(1, 1)
        AA6 = o.number(1)
        AA7 = o.number(2)
        NL10 = o.zeros(n, l)
        NK11 = o.zeros(n, k)
        KK12 = o.zeros(k, k)
        AA13 = o.zeros(1, 1)
        AA14 = o.zeros(1, 1)
        LL15 = o.zeros(l, l)
        KL16 = o.zeros(k, l)
        KK17 = o.zeros(k, k)
        NK18 = o.zeros(n, k)
        KK19 = o.zeros(k, k)
        AA20 = o.zeros(1, 1)
        AA21 = o.zeros(1, 1)
        AA22 = o.zeros(1, 1)
        MK25 = o.zeros(m, k)
        ML26 = o.zeros(m, l)
        KK27 = o.zeros(k, k)
        KL28 = o.zeros(k, l)
        LL29 = o.zeros(l, l)
        ML30 = o.zeros(m, l)
        KL32 = o.zeros(k, l)
        LL33 = o.zeros(l, l)
        KL34 = o.zeros(k, l)
        KN35 = o.zeros(k, n)
        notify = o.number(0)
        
        MC = o.number(o.get_mem_info() - self.initial_memory)
        o.rank_reduce(MC)
        if self.rank == 0:
            print "Memory consumption %d MB" % MC.fetch()
        
        if print_err:
            o.norm2(X, AA5)
            o.reduce_(AA5, 'ij')
        
        for it in range(self.max_iter):
            o.it = it
            if self.rank == 0 and self.check_stop(E=E, history=h):
                notify = o.number(1)
                self.number_of_iterations = it

            o.sync_(notify, 'i')
            o.sync_(notify, 'j')
                
            if notify.fetch()[0,0] == 1:
                if self.rank == 0:
                    print "Stopping criteria reached after %d iterations" % it
                break
            
            if it == 2 and self.sync == False:
                self.operation.sync_matrix = self.operation.empty_sync_matrix
                self.operation.mreduce = self.operation.empty_mreduce
            
            if it == 2:
                self.timer.split('main')
            
            o.sync_(V, 'j')
            o.dot_wrapper('nmk', X, V, NL10)
            o.reduce_(NL10, 'i')
            o.sync_0i(S)
            o.dot_wrapper('nkk', NL10, S, NK11, transb='T')
            o.dot_wrapper('knk', NK11, U, KK12, transa='T')
            o.reduce_0i(KK12)
            o.dot_wrapper('kmk', V, V, LL15, transa='T')
            o.reduce_0j(LL15)
            o.dot_wrapper('kkk', S, LL15, KL16)
            o.dot_wrapper('kkk', KL16, S, KK17, transb='T')
            o.sync_0i(KK17)
            o.dot_wrapper('nkk', U, KK17, NK18)
            o.dot_wrapper('knk', U, NK18, KK19, transa='T')
            if print_err:
                o.reduce_0i(KK19)
                o.trace(KK12, AA13)
                o.multiply(AA7, AA13, AA14)    
                o.trace(KK19, AA20)
                o.sub(AA14, AA20, AA21)
                o.divide(AA21, AA5, AA22)
                o.sub(AA6, AA22, E)
            o.kernel_wrapper_lin('nk', NK11, NK18, U)
            o.sync_(U, 'i')
            o.dot_wrapper('mnk', X, U, MK25, transa='T')
            o.reduce_(MK25, 'j')
            o.sync_0j(S)
            o.dot_wrapper('mkk', MK25, S, ML26)
            o.dot_wrapper('knk', U, U, KK27, transa='T')
            o.reduce_0i(KK27)
            o.dot_wrapper('kkk', KK27, S, KL28)
            o.dot_wrapper('kkk', S, KL28, LL29, transa='T')
            o.sync_0j(LL29)
            o.dot_wrapper('mkk', V, LL29, ML30)
            o.kernel_wrapper_lin('mk', ML26, ML30, V)
            o.dot_wrapper('kmk', MK25, V, KL32, transa='T')
            o.reduce_0j(KL32)
            o.dot_wrapper('kmk', V, V, LL33, transa='T')
            o.reduce_0j(LL33)
            o.dot_wrapper('kkk', KL28, LL33, KL34)
            o.kernel_wrapper_lin('kk', KL32, KL34, S)

            if print_err:
                if self.rank == 0:
                    e = E.fetch(key=(0,0))
                    err = e[0,0]
                    h.append(err)
                    if it == 0:
                        print "Frobenius norm at iteration:"
                    else:
                        print '%d:' % it, np.float64(err)

        return h

    @factorization
    def run_nmtf_ding(self, X=None, U=None, S=None, V=None, E=None, n=None, 
        m=None, k=None, l=None, debug=None, print_err=False):
        o = self.operation
        h = []
    
        AA5 = o.zeros(1, 1)
        AA6 = o.number(1)
        AA7 = o.number(2)
        NL10 = o.zeros(n, l)
        NK11 = o.zeros(n, k)
        KK12 = o.zeros(k, k)
        AA13 = o.zeros(1, 1)
        AA14 = o.zeros(1, 1)
        KK15 = o.zeros(k, k)
        LL16 = o.zeros(l, l)
        KL17 = o.zeros(k, l)
        KL18 = o.zeros(k, l)
        KK19 = o.zeros(k, k)
        AA20 = o.zeros(1, 1)
        AA21 = o.zeros(1, 1)
        AA22 = o.zeros(1, 1)
        NK24 = o.zeros(n, k)
        MK26 = o.zeros(m, k)
        ML27 = o.zeros(m, l)
        LL28 = o.zeros(l, l)
        ML29 = o.zeros(m, l)
        KL31 = o.zeros(k, l)
        KK32 = o.zeros(k, k)
        LL33 = o.zeros(l, l)
        KL34 = o.zeros(k, l)
        KL35 = o.zeros(k, l)
        notify = o.number(0)
        
        MC = o.number(o.get_mem_info() - self.initial_memory)
        o.rank_reduce(MC)
        if self.rank == 0:
            print "Memory consumption %d MB" % MC.fetch()
        
        if print_err:
            o.norm2(X, AA5)
            o.reduce_(AA5, 'ij')
        
        
        for it in range(self.max_iter):
            o.it = it
            if self.rank == 0 and self.check_stop(E=E, history=h):
                notify = o.number(1)
                self.number_of_iterations = it

            o.sync_(notify, 'i')
            o.sync_(notify, 'j')
                
            if notify.fetch()[0,0] == 1:
                if self.rank == 0:
                    print "Stopping criteria reached after %d iterations" % it 
                break
            
            if it == 2 and self.sync == False:
                self.operation.sync_matrix = self.operation.empty_sync_matrix
                self.operation.mreduce = self.operation.empty_mreduce
            
            if it == 2:
                self.timer.split('main')
            
            
            o.sync_(V, 'j')
            o.dot_wrapper('nmk', X, V, NL10)
            o.reduce_(NL10, 'i')
            o.sync_0i(S)
            o.dot_wrapper('nkk', NL10, S, NK11, transb='T')
            o.dot_wrapper('knk', NK11, U, KK12, transa='T')
            o.reduce_0i(KK12)
            if print_err:
                o.dot_wrapper('knk', U, U, KK15, transa='T')
                o.reduce_0i(KK15)
                o.dot_wrapper('kmk', V, V, LL16, transa='T')
                o.reduce_0j(LL16)
                o.dot_wrapper('kkk', KK15, S, KL17)
                o.dot_wrapper('kkk', KL17, LL16, KL18)
                o.dot_wrapper('kkk', KL18, S, KK19, transb='T')
                o.trace(KK12, AA13)
                o.multiply(AA7, AA13, AA14)
                o.trace(KK19, AA20)
                o.sub(AA14, AA20, AA21)
                o.divide(AA21, AA5, AA22)
                o.sub(AA6, AA22, E)
            o.sync_0i(KK12)
            o.dot_wrapper('nkk', U, KK12, NK24, transb='T')
            o.kernel_wrapper('nk', NK11, NK24, U)
            o.sync_(U, 'i')
            o.dot_wrapper('mnk', X, U, MK26, transa='T')
            o.reduce_(MK26, 'j')
            o.sync_0j(S)
            o.dot_wrapper('mkk', MK26, S, ML27)
            o.dot_wrapper('kmk', V, ML27, LL28, transa='T')
            o.reduce_0j(LL28)
            o.sync_0j(LL28)
            o.dot_wrapper('mkk', V, LL28, ML29)
            o.kernel_wrapper('mk', ML27, ML29, V)
            o.dot_wrapper('kmk', MK26, V, KL31, transa='T')
            o.reduce_0j(KL31)
            o.dot_wrapper('knk', U, U, KK32, transa='T')
            o.reduce_0i(KK32)
            o.dot_wrapper('kmk', V, V, LL33, transa='T')
            o.reduce_0j(LL33)
            o.dot_wrapper('kkk', KK32, S, KL34)
            o.dot_wrapper('kkk', KL34, LL33, KL35)
            o.kernel_wrapper('kk', KL31, KL35, S)
                        
            if print_err:
                if self.rank == 0:
                    e = E.fetch(key=(0,0))
                    err = e[0,0]
                    h.append(err)
                    if it == 0:
                        print "Frobenius norm at iteration:"
                    else:
                        print '%d:' % it, np.float64(err)
                        
        return h


        