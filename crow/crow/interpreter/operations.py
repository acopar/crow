import numpy as np
from matrix import *

class Position():
    def __init__(self, colA=None, colB=None, rowA=None, rowB=None):
        self.colA = colA
        self.colB = colB
        self.rowA = rowA
        self.rowB = rowB
    
    def isActive(self):
        if self.colA != None or self.colB != None or self.rowA != None or self.rowB != None:
            return True
        return False
    
    def notActive(self):
        if self.colA == None and self.colB == None and self.rowA == None and self.rowB == None:
            return True
        return False
    
    def getColA(self):
        return np.int32(self.colA)
    
    def getColB(self):
        return np.int32(self.colB)
    
    def getRowA(self):
        return np.int32(self.rowA)
    
    def getRowB(self):
        return np.int32(self.rowB)
    
    def __str__(self):
        return '(%s,%s), (%s,%s)' % (str(self.rowA), str(self.colA), str(self.rowB), str(self.colB))

def vertical_operation(f):
    def new_f(*args, **kwargs):
        self = args[0]
        if self.bid[1] == 0:
            f(*args, **kwargs)
    return new_f

def horizontal_operation(f):
    def new_f(*args, **kwargs):
        self = args[0]
        if self.bid[0] == 0:
            f(*args, **kwargs)
    return new_f

def block_operation(f):
    def new_f(*args, **kwargs):
        self = args[0]
        if self.bid == (0,0):
            f(*args, **kwargs)
    return new_f

class Operation(object):
    def __init__(self, rank, rev_map, iblock_map, jblock_map, tblock_map):
        self.__dict__.update(locals())
        self.__dict__.pop('self', None)
        self.dot_mapper = {
            'nmk': self.bigdot_wrapper,
            'mnk': self.bigdot_wrapper,
            'nnk': self.bigdot_wrapper,
            'nm1': self.bigdot_wrapper,
            'mn1': self.bigdot_wrapper,
            'nkk': self.dot_vertical,
            'kkn': self.dot_vertical,
            'knk': self.dot_vertical,
            'nk1': self.dot_vertical,
            '1m1': self.dot_vertical,
            'mkk': self.dot_horizontal,
            'kkm': self.dot_horizontal,
            'kmk': self.dot_horizontal,
            'mk1': self.dot_horizontal,
            'kkk': self.dot_block,
            '1kk': self.dot_block,
            '1k1': self.dot_block,
            'k1k': self.dot_vectors,
            'nkm': self.dot_all,
            'mkn': self.dot_all,
            'n1m': self.dot_all,
            'm1n': self.dot_all,
            'nkn': self.dot_nkn
        }
    
    def dot_wrapper(self, dim, A, B, C, transa='N', transb='N', pos=None):
        func = None
        if dim in self.dot_mapper:
            func = self.dot_mapper[dim]
        else:
            raise Exception("Error: Unsupported dot dimensions %s" % dim)
        
        func(A, B, C, transa=transa, transb=transb)
    
    def kernel_wrapper(self, dim, A, B, C, transa='N', transb='N'):
        if dim == 'nk':
            if self.bid[1] == 0:
                self.kernel(A.get(), B.get(), C.get(), transa='N')
        elif dim == 'mk':
            if self.bid[0] == 0:
                self.kernel(A.get(), B.get(), C.get(), transa='N')
        elif dim == 'kk':
            if self.bid == (0,0):
                self.kernel(A.get(), B.get(), C.get(), transa='N')
    
    def transpose(self, A, C, transa='N', pos=None):
        C.set(self._tr(A.get()))
    
    def divide(self, A, B, C, pos=None):
        C.set(self._divide(A.get(), B.get(), C.get()))
    
    def sub(self, A, B, C, pos=None):
        C.set(self._sub(A.get(), B.get(), C.get()))
    
    def add(self, A, B, C, pos=None):
        C.set(self._add(A.get(), B.get(), C.get()))

    def multiply(self, A, B, C, pos=None):
        C.set(self._multiply(A.get(), B.get(), C.get()))
    
    def square(self, A, C, transa='N', pos=None):
        self.multiply(A, A, C)
    
    def sqrt(self, A, C, transa='N', pos=None):
        self._sqrt(A.get(), C.get())
    
    def inverse(self, A, C, transa='N', pos=None):
        C.set(self._inverse(A.get(), C.get()))
    
    def norm1(self, A, C, transa='N', pos=None):
        self.sum(A, C)
        
    def norm2(self, A, C, transa='N', pos=None):
        raise Exception("Unimplemented norm2")
    
    def project(self, A, C, transa='N', pos=None):
        C.set(self._project(A.get(), C.get(), transa=transa))
    
    def log(self, A, C, transa='N', pos=None):
        C.set(self._log(A.get(), C.get(), transa=transa))
    
    def vsum(self, dim, A, C, transa='N', pos=None):
        if dim == 'nk':
            if self.bid[1] == 0:
                C.set(self._axis_sum(A.get(), C.get(), transa=transa))
        elif dim == 'mk':
            if self.bid[0] == 0:
                C.set(self._axis_sum(A.get(), C.get(), transa=transa))
        elif dim == 'kk':
            if self.bid == (0,0):
                C.set(self._axis_sum(A.get(), C.get(), transa=transa))
    
    def sum(self, A, C):
        C.set(self._sum(A.get(), C.get()))
    
    def bigdot_wrapper(self, A, B, C, transa='N', transb='N', pos=None):
        if A.hasTransposed() and transa == 'T':
            A = A.get(transa=transa)
            C.set(self.bigdot(A, B.get(), C.get(), transb=transb))
        else:
            C.set(self.bigdot(A.get(), B.get(), C.get(), transa=transa, transb=transb))
    
    @vertical_operation
    def dot_vertical(self, A, B, C, transa='N', transb='N', pos=None):
        C.set(self.dot(A.get(), B.get(), C.get(), transa=transa, transb=transb))
    
    @horizontal_operation         
    def dot_horizontal(self, A, B, C, transa='N', transb='N', pos=None):
        C.set(self.dot(A.get(), B.get(), C.get(), transa=transa, transb=transb))
    
    @block_operation
    def dot_block(self, A, B, C, transa='N', transb='N', pos=None):
        C.set(self.dot(A.get(), B.get(), C.get(), transa=transa, transb=transb))
           
    @block_operation
    def dot_vectors(self, A, B, C, transa='N', transb='N', pos=None):
        C.set(self.dot(A.get(), B.get(), C.get(), transa=transa, transb=transb))
    
    def dot_all(self, A, B, C, transa='N', transb='N', pos=None):
        C.set(self.dot(A.get(), B.get(), C.get(), transa=transa, transb=transb))
    
    def dot_nkn(self, A, B, C, transa='N', transb='N', pos=None):
        bid1 = (self.bid[0], 0)
        bid2 = (self.bid[1], 0)
        A = A.get(key=bid1)
        B = B.get(key=bid2)
        C.set(self.dot(A, B, C.get(), transa=transa, transb=transb))

    def sync_(self, A, axis):
        device_list = []
        source = None
        dev = self.rev_map
        bid = self.bid
        
        if axis == 'i':
            device_list = self.iblock_map[bid]
            source = (bid[0], 0)
        elif axis == 'j':
            device_list = self.jblock_map[bid]
            source = (0, bid[1])
        elif axis == 't':
            device_list = self.tblock_map[bid]
            source = (bid[1], 0)
        else:
            raise Exception("Unsupported axis in synchronization: %s" % axis)
        
        if bid == source:
            output = A[bid]
            for b in device_list:
                if dev[b] != dev[source]:
                    self.sync_only()
                    self.send(A[bid], dev[b])
                else:
                    kmp = self.zeros_function(*output.shape)
                    kmp += A[bid]
                    A[b] = kmp
        else:
            if dev[bid] != dev[source]:
                self.recv(A[bid], dev[source])
    
    def reduce_(self, A, axis, debug=False):
        device_list = []
        source = None
        dev = self.rev_map
        bid = self.bid
        
        if axis == 'i':
            device_list = self.iblock_map[bid]
            source = (bid[0], 0)
        elif axis == 'j':
            device_list = self.jblock_map[bid]
            source = (0, bid[1])
        elif axis == 'ij':
            device_list = sorted(self.rev_map.keys())
            device_list = [x for x in device_list if x != (0, 0)]
            source = (0, 0)
        else:
            raise Exception("Unsupported axis in reduction: %s" % axis)
        
        if bid == source:
            if debug:
                print bid, device_list, source
            kmp = None
            output = A[bid]
            if len(device_list) > 0:
                kmp = self.zeros_function(*output.shape)
            
            for b in device_list:
                if dev[b] != dev[source]:
                    self.recv(kmp, dev[b])
                    output += kmp
                else:
                    output += A[b]
        else:
            if dev[bid] != dev[source]:
                self.sync_only()
                self.send(A[bid], dev[source])
    
    @vertical_operation
    def sync_0i(self, C):
        self.sync_(C, 'j')
    
    @horizontal_operation
    def sync_0j(self, C):
        self.sync_(C, 'i')
    
    @vertical_operation
    def reduce_0i(self, C):
        self.reduce_(C, 'j')
    
    @horizontal_operation
    def reduce_0j(self, C):
        self.reduce_(C, 'i')
    
    def sreduce(self, A):
        self.reduce_(A, 'ij')
    
    def assign(self, A, B, pos=None):
        #self.assign_(A, B)
        A.set(B.get(col=pos.colB,row=pos.rowB), col=pos.colA, row=pos.rowA)
    
    def matrix(self, X, Xt=None):
        mat = None
        for key in X:
            data = X[key]
            if mat == None:
                mat = Matrix(data[0], Xt=data[1], key=key)
            else:
                mat.append(data[0], Xt=data[1], key=key)
        if mat == None:
            raise Exception("Error creating matrix operator")
        return mat
    
    def zeros(self, x, y=0):
        return Matrix(self.zeros_function(x, y), key=self.bid)

    def block_zeros(self, dim_x, dim_y, block_map, model='ij'):
        mat = None
        for bid in block_map:
            if type(dim_x) == type({}):
                x = dim_x[bid]
            else:
                x = dim_x
            if type(dim_y) == type({}):
                y = dim_y[bid]
            else:
                y = dim_y
            
            if mat == None:
                mat = Matrix(self.zeros_function(x, y), key=bid, model=model)
            else:
                mat.append(self.zeros_function(x, y), key=bid)
        return mat
