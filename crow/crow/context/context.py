from crow.utils import Timer
from crow.transfer.cputransfer import cpu_reduce
from crow.utils import *
from crow.config import *

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
        kwargs['n'] = self.dimensions['n'][bid]
        kwargs['m'] = self.dimensions['m'][bid]
        kwargs['k'] = self.dimensions['k'][bid]
        kwargs['l'] = self.dimensions['l'][bid]

        self.timer = Timer()
        self.operation.load_kernel()
        self.operation.sync_flag = self.sync
        
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
        self.prev = None
        self.now = None
        
        self.max_iter = config['max_iter']
        self.balanced = True
        if config['unbalanced']:
            self.balanced = False
        self.timer = Timer()
        self.nb = config['nb']
        self.mb = config['mb']
        self.multiplier = (1, 1)
        
        if self.balanced == True:
            self.data_folder = to_path(inputs['data'], '%d_%d' % (self.nb, self.mb))
        else:
            self.data_folder = to_path(inputs['data'], 'u%d_%d' % (self.nb, self.mb))
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
    
    def get_blocks(self):
        return self.block_map[0]

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
        
        def set_matrix(X, bid, v, dim):
            if v not in self.storage:
                self.storage[v] = {}
            self.storage[v][bid] = X
            if dim[0] not in self.dimensions:
                self.dimensions[dim[0]] = {}
            self.dimensions[dim[0]][bid] = X.shape[0]
            
            if dim[1] not in self.dimensions:
                self.dimensions[dim[1]] = {}
            self.dimensions[dim[1]][bid] = X.shape[1]
        
        def new_matrix(bid, v, dim):
            dim = sizes[v]
            x = get_dimension(self.dimensions, dim[0], bid)
            y = get_dimension(self.dimensions, dim[1], bid)
            if v not in self.storage:
                self.storage[v] = {}
            self.storage[v][bid] = self.operation.czeros(x,y)
        
        for idx, jdx in self.block_map[0]:
            bid = (idx, jdx)
            
            if data == True:
                for v in data_vars:
                    filename = to_path(self.data_folder, '%d_%d.npz' % (idx, jdx))
                    #X, Xt = self.load_dataset(filename, self.dense)
                    X = self.load_data(filename, self.dense)
                    set_matrix(X, bid, v, sizes[v])
            
            factor_file = to_path(self.factor_folder, '%d_%d.pkl' % (idx, jdx))
            factors = load_file(factor_file)
            
            for v in factor_vars:
                set_matrix(factors[v], bid, v, sizes[v])
                
            for v in error_vars:
                new_matrix(bid, v, sizes[v])

            for v in empty_vars:
                new_matrix(bid, v, sizes[v])
            
            for v in param_vars:
                dim = sizes[v]
                if v not in self.dimensions:
                    raise Exception("Undefined parameter %s" % v)
                p = self.dimensions[v]
                x = get_dimension(self.dimensions, dim[0], bid)
                y = get_dimension(self.dimensions, dim[1], bid)
                if v not in self.storage:
                    self.storage[v] = {}
                self.storage[v][bid] = self.operation.czeros(x,y) + p
    
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
    
    def save(self, output, results, data):
        if not output is None:
            dump_file(output, data)
        
        output_vars = self.factor_vars + self.error_vars
        results_folder = results
        if not results_folder is None:
            for key in output_vars:
                storage_folder = to_path(results_folder, key)
                for bid in self.storage[key]:
                    storage_out = to_path(storage_folder, '%d_%d.pkl' % (bid[0], bid[1]))
                    dump_file(storage_out, self.storage[key][bid])
    
    
    def check_stop(self, E=None):
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
        self.prev = self.now
    
    @factorization
    def run_nmtf_long(self, X=None, U=None, S=None, V=None, E=None, n=None, 
        m=None, k=None, l=None, debug=None, print_err=False):
        o = self.operation
        h = []
        
        MK4 = o.zeros(m, k)
        NK5 = o.zeros(n, k)
        KK6 = o.zeros(k, k)
        NK7 = o.zeros(n, k)
        NK8 = o.zeros(n, k)
        NK9 = o.zeros(n, k)
        MK11 = o.zeros(m, k)
        ML12 = o.zeros(m, l)
        KK13 = o.zeros(k, k)
        KL14 = o.zeros(k, l)
        ML15 = o.zeros(m, l)
        ML16 = o.zeros(m, l)
        ML17 = o.zeros(m, l)
        KL19 = o.zeros(k, l)
        LL20 = o.zeros(l, l)
        KL21 = o.zeros(k, l)
        KL22 = o.zeros(k, l)
        KL23 = o.zeros(k, l)
        notify = o.number(0)
        AA11 = o.zeros(1,1)
        AA12 = o.number(n*k)
        
        for it in range(self.max_iter):
            o.it = it
            if self.rank == 0 and self.check_stop(E=E):
                print self.check_stop(E=E)
                notify = o.number(1)
                o.sync_(notify, 'i')
                o.sync_(notify, 'j')
                self.number_of_iterations = it
                
            if notify.fetch()[0,0] == 1:
                print "Stopping criteria reached after %d iterations" % it
                break
            
            if it == 2 and self.sync == False:
                o.sync_matrix = o.empty_sync_matrix
                o.mreduce = o.empty_mreduce
            
            if it == 2:
                self.timer.split('main')
            
            o.sync_0j(S)
            o.dot_wrapper('mkk', V, S, MK4, transb='T')
            o.sync_(MK4, 'j')
            o.dot_wrapper('nmk', X, MK4, NK5)
            o.reduce_(NK5, 'i')
            o.dot_wrapper('kmk', MK4, MK4, KK6, transa='T')
            o.reduce_0j(KK6)
            o.sync_0i(KK6)
            o.dot_wrapper('nkk', U, KK6, NK7)
            o.kernel_wrapper('nk', NK5, NK7, U)
            o.norm1(U, AA11, transa='N')
            o.reduce_(AA11, 'i')
            o.divide(AA11, AA12, E)
            o.sync_(U, 'i')
            o.dot_wrapper('mnk', X, U, MK11, transa='T')
            o.reduce_(MK11, 'j')
            o.dot_wrapper('mkk', MK11, S, ML12)
            o.dot_wrapper('knk', U, U, KK13, transa='T')
            o.reduce_0i(KK13)
            o.dot_wrapper('kkk', KK13, S, KL14)
            o.sync_0j(KL14)
            o.dot_wrapper('mkk', MK4, KL14, ML15)
            o.kernel_wrapper('mk', ML12, ML15, V)
            o.dot_wrapper('kmk', MK11, V, KL19, transa='T')
            o.reduce_0j(KL19)
            o.dot_wrapper('kmk', V, V, LL20, transa='T')
            o.reduce_0j(LL20)
            o.dot_wrapper('kkk', KL14, LL20, KL21)
            o.kernel_wrapper('kk', KL19, KL21, S)
        
        return h
    
    
    @factorization
    def run_nmtf_long_err(self, X=None, U=None, S=None, V=None, E=None, n=None, 
        m=None, k=None, l=None, debug=None, print_err=False):
        o = self.operation
        h = []
        
        KM5 = o.zeros(k, m)
        NM6 = o.zeros(n, m)
        NM7 = o.zeros(n, m)
        NM8 = o.zeros(n, m)
        AA9 = o.zeros(1, 1)
        NM10 = o.zeros(n, m)
        AA11 = o.zeros(1, 1)
        NK13 = o.zeros(n, k)
        KK14 = o.zeros(k, k)
        NK15 = o.zeros(n, k)
        NK16 = o.zeros(n, k)
        NK17 = o.zeros(n, k)
        MK19 = o.zeros(m, k)
        ML20 = o.zeros(m, l)
        KK21 = o.zeros(k, k)
        KL22 = o.zeros(k, l)
        ML23 = o.zeros(m, l)
        ML24 = o.zeros(m, l)
        ML25 = o.zeros(m, l)
        KL27 = o.zeros(k, l)
        LL28 = o.zeros(l, l)
        KL29 = o.zeros(k, l)
        KL30 = o.zeros(k, l)
        KL31 = o.zeros(k, l)
        notify = o.number(0)
        
        for it in range(self.max_iter):
            o.it = it
            if self.rank == 0 and self.check_stop(E=E):
                notify = o.number(1)
                o.sync_(notify, 'i')
                o.sync_(notify, 'j')
                self.number_of_iterations = it
            
            if notify.fetch()[0,0] == 1:
                print "Stopping criteria reached after %d iterations" % it
                break
            
            if it == 2 and self.sync == False:
                o.sync_matrix = o.empty_sync_matrix
                o.mreduce = o.empty_mreduce
            
            if it == 2:
                self.timer.split('main')

            if print_err:
                e = E.fetch(key=bid)
                err = e[0,0]
                
                if self.rank == 0:
                    if it == 0:
                        print "Frobenius norm at iteration:"
                    else:
                        print '%d:' % it, float(err)
                        h.append(err)
            
            
            o.sync_0j(S)
            o.dot_wrapper('kkm', S, V, KM5, transb='T', transa='N')
            o.sync_(U, 'i')
            o.sync_(KM5, 'j')
            o.dot_wrapper('nkm', U, KM5, NM6, transb='N', transa='N')
            o.sub(X, NM6, NM7)
            o.square(NM7, NM8, transa='N')
            o.norm1(NM8, AA9, transa='N')
            o.reduce_(AA9, 'ij')
            o.square(X, NM10, transa='N')
            o.norm1(NM10, AA11, transa='N')
            o.reduce_(AA11, 'ij')
            o.divide(AA9, AA11, E)
            o.sync_(KM5, 'j')
            o.dot_wrapper('nmk', X, KM5, NK13, transb='T', transa='N')
            o.reduce_(NK13, 'i')
            o.dot_wrapper('kmk', KM5, KM5, KK14, transb='T', transa='N')
            o.reduce_0j(KK14)
            o.sync_0i(KK14)
            o.dot_wrapper('nkk', U, KK14, NK15, transb='N', transa='N')
            o.divide(NK13, NK15, NK16)
            o.sqrt(NK16, NK17, transa='N')
            o.multiply(U, NK17, U)
            o.sync_(U, 'i')
            o.dot_wrapper('mnk', X, U, MK19, transb='N', transa='T')
            o.reduce_(MK19, 'j')
            o.dot_wrapper('mkk', MK19, S, ML20, transb='N', transa='N')
            o.dot_wrapper('knk', U, U, KK21, transb='N', transa='T')
            o.reduce_0i(KK21)
            o.dot_wrapper('kkk', KK21, S, KL22, transb='N', transa='N')
            o.sync_0j(KL22)
            o.dot_wrapper('mkk', KM5, KL22, ML23, transb='N', transa='T')
            o.divide(ML20, ML23, ML24)
            o.sqrt(ML24, ML25, transa='N')
            o.multiply(V, ML25, V)
            o.dot_wrapper('kmk', MK19, V, KL27, transb='N', transa='T')
            o.reduce_0j(KL27)
            o.dot_wrapper('kmk', V, V, LL28, transb='N', transa='T')
            o.reduce_0j(LL28)
            o.dot_wrapper('kkk', KL22, LL28, KL29, transb='N', transa='N')
            o.divide(KL27, KL29, KL30)
            o.sqrt(KL30, KL31, transa='N')
            o.multiply(S, KL31, S)
        
        return h
    

    @factorization
    def run_nmtf_ding(self, X=None, U=None, S=None, V=None, E=None, n=None, 
        m=None, k=None, l=None, debug=None, print_err=False):
        o = self.operation
        h = []
        
        MK4 = o.zeros(m, k)
        NK5 = o.zeros(n, k)
        KK6 = o.zeros(k, k)
        NK7 = o.zeros(n, k)
        NK8 = o.zeros(n, k)
        NK9 = o.zeros(n, k)
        MK11 = o.zeros(m, k)
        ML12 = o.zeros(m, l)
        LL13 = o.zeros(l, l)
        ML14 = o.zeros(m, l)
        ML15 = o.zeros(m, l)
        ML16 = o.zeros(m, l)
        KL18 = o.zeros(k, l)
        KK19 = o.zeros(k, k)
        LL20 = o.zeros(l, l)
        KL21 = o.zeros(k, l)
        KL22 = o.zeros(k, l)
        KL23 = o.zeros(k, l)
        KL24 = o.zeros(k, l)
        notify = o.number(0)
        AA11 = o.zeros(1,1)
        AA12 = o.number(n*k)
        
        for it in range(self.max_iter):
            o.it = it
            if self.rank == 0 and self.check_stop(E=E):
                notify = o.number(1)
                o.sync_(notify, 'i')
                o.sync_(notify, 'j')
                self.number_of_iterations = it
                
            if notify.fetch()[0,0] == 1:
                print "Stopping criteria reached after %d iterations" % it
                break
            
            if it == 2 and self.sync == False:
                o.sync_matrix = o.empty_sync_matrix
                o.mreduce = o.empty_mreduce
            
            if it == 2:
                self.timer.split('main')
            
            o.sync_0j(S)
            o.dot_wrapper('mkk', V, S, MK4, transb='T', transa='N')
            o.sync_(MK4, 'j')
            o.dot_wrapper('nmk', X, MK4, NK5, transb='N', transa='N')
            o.reduce_(NK5, 'i')
            o.dot_wrapper('knk', U, NK5, KK6, transb='N', transa='T')
            o.reduce_0i(KK6)
            o.sync_0i(KK6)
            o.dot_wrapper('nkk', U, KK6, NK7, transb='N', transa='N')
            o.kernel_wrapper('nk', NK5, NK7, U)
            o.norm1(U, AA11, transa='N')
            o.reduce_(AA11, 'i')
            o.divide(AA11, AA12, E)
            o.sync_(U, 'i')
            o.dot_wrapper('mnk', X, U, MK11, transb='N', transa='T')
            o.reduce_(MK11, 'j')
            o.dot_wrapper('mkk', MK11, S, ML12, transb='N', transa='N')
            o.dot_wrapper('kmk', V, ML12, LL13, transb='N', transa='T')
            o.reduce_0j(LL13)
            o.sync_0j(LL13)
            o.dot_wrapper('mkk', V, LL13, ML14, transb='N', transa='N')
            o.kernel_wrapper('mk', ML12, ML14, V)
            o.dot_wrapper('kmk', MK11, V, KL18, transb='N', transa='T')
            o.reduce_0j(KL18)
            o.dot_wrapper('knk', U, U, KK19, transb='N', transa='T')
            o.reduce_0i(KK19)
            o.dot_wrapper('kmk', V, V, LL20, transb='N', transa='T')
            o.reduce_0j(LL20)
            o.dot_wrapper('kkk', KK19, S, KL21, transb='N', transa='N')
            o.dot_wrapper('kkk', KL21, LL20, KL22, transb='N', transa='N')
            o.kernel_wrapper('kk', KL18, KL22, S)
        
        return h
        
    @factorization
    def run_nmtf_ding_err(self, X=None, U=None, S=None, V=None, E=None, n=None, 
        m=None, k=None, l=None, debug=None, print_err=False):
        o = self.operation
        h = []
    
        KM5 = o.zeros(k, m)
        NM6 = o.zeros(n, m)
        NM7 = o.zeros(n, m)
        NM8 = o.zeros(n, m)
        AA9 = o.zeros(1, 1)
        NM10 = o.zeros(n, m)
        AA11 = o.zeros(1, 1)
        NK13 = o.zeros(n, k)
        KK14 = o.zeros(k, k)
        NK15 = o.zeros(n, k)
        NK16 = o.zeros(n, k)
        NK17 = o.zeros(n, k)
        MK19 = o.zeros(m, k)
        ML20 = o.zeros(m, l)
        LL21 = o.zeros(l, l)
        ML22 = o.zeros(m, l)
        ML23 = o.zeros(m, l)
        ML24 = o.zeros(m, l)
        KL26 = o.zeros(k, l)
        KK27 = o.zeros(k, k)
        LL28 = o.zeros(l, l)
        KL29 = o.zeros(k, l)
        KL30 = o.zeros(k, l)
        KL31 = o.zeros(k, l)
        KL32 = o.zeros(k, l)
        notify = o.number(0)
        
        for it in range(self.max_iter):
            o.it = it
            if self.rank == 0 and self.check_stop(E=E):
                notify = o.number(1)
                o.sync_(notify, 'i')
                o.sync_(notify, 'j')
                self.number_of_iterations = it
                
            if notify.fetch()[0,0] == 1:
                print "Stopping criteria reached after %d iterations" % it
                break
            
            if it == 2 and self.sync == False:
                self.operation.sync_matrix = self.operation.empty_sync_matrix
                self.operation.mreduce = self.operation.empty_mreduce
            
            if it == 2:
                self.timer.split('main')
            
            if print_err:
                e = E.fetch(key=bid)
                err = e[0,0]
                
                if self.rank == 0:
                    if it == 0:
                        print "Frobenius norm at iteration:"
                    else:
                        print '%d:' % it, float(err)
                        h.append(err)
            
            o.sync_0j(S)
            o.dot_wrapper('kkm', S, V, KM5, transb='T', transa='N')
            o.sync_(U, 'i')
            o.sync_(KM5, 'j')
            o.dot_wrapper('nkm', U, KM5, NM6, transb='N', transa='N')
            o.sub(X, NM6, NM7)
            o.square(NM7, NM8, transa='N')
            o.norm1(NM8, AA9, transa='N')
            o.reduce_(AA9, 'ij')
            o.square(X, NM10, transa='N')
            o.norm1(NM10, AA11, transa='N')
            o.reduce_(AA11, 'ij')
            o.divide(AA9, AA11, E)
            o.sync_(KM5, 'j')
            o.dot_wrapper('nmk', X, KM5, NK13, transb='T', transa='N')
            o.reduce_(NK13, 'i')
            o.dot_wrapper('knk', U, NK13, KK14, transb='N', transa='T')
            o.reduce_0i(KK14)
            o.sync_0i(KK14)
            o.dot_wrapper('nkk', U, KK14, NK15, transb='N', transa='N')
            o.divide(NK13, NK15, NK16)
            o.sqrt(NK16, NK17, transa='N')
            o.multiply(U, NK17, U)
            o.sync_(U, 'i')
            o.dot_wrapper('mnk', X, U, MK19, transb='N', transa='T')
            o.reduce_(MK19, 'j')
            o.dot_wrapper('mkk', MK19, S, ML20, transb='N', transa='N')
            o.dot_wrapper('kmk', V, ML20, LL21, transb='N', transa='T')
            o.reduce_0j(LL21)
            o.sync_0j(LL21)
            o.dot_wrapper('mkk', V, LL21, ML22, transb='N', transa='N')
            o.divide(ML20, ML22, ML23)
            o.sqrt(ML23, ML24, transa='N')
            o.multiply(V, ML24, V)
            o.dot_wrapper('kmk', MK19, V, KL26, transb='N', transa='T')
            o.reduce_0j(KL26)
            o.dot_wrapper('knk', U, U, KK27, transb='N', transa='T')
            o.reduce_0i(KK27)
            o.dot_wrapper('kmk', V, V, LL28, transb='N', transa='T')
            o.reduce_0j(LL28)
            o.dot_wrapper('kkk', KK27, S, KL29, transb='N', transa='N')
            o.dot_wrapper('kkk', KL29, LL28, KL30, transb='N', transa='N')
            o.divide(KL26, KL30, KL31)
            o.sqrt(KL31, KL32, transa='N')
            o.multiply(S, KL32, S)
        
        return h
        