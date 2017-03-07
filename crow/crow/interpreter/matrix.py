import numpy as np
import scipy

class Matrix():
    def __init__(self, X, Xt=None, key=None, model='ij'):
        self.blocks = {}
        self.blocks_t = {}
        self.X = X
        self.Xt = Xt
        
        self.key = key
        self.model = model
        self.append(X, Xt=Xt, key=key)
        
        self.type = 'gpu'
        if type(self.X) == np.ndarray or type(self.X) == scipy.sparse.csr.csr_matrix:
            self.type = 'cpu'
        elif type(self.X) == np.matrixlib.defmatrix.matrix:
            print "Warning: using matrixlib.defmatrix.matrix type"
            self.type = 'cpu'
    
    def get(self, transa='N', key=None, col=None, row=None):
        if key is None:
            key = self.key
        
        X = None
        if transa == 'T':
            if key in self.blocks_t:
                X = self.blocks_t[key]
            else:
                if key in self.blocks:
                    X = self.blocks[key].T
        else:
            if key in self.blocks:
                X = self.blocks[key]
            else:
                print 'Warning: get will return None'
        return X
    
    def fetch(self, key=None):
        if key is None:
            key = self.key
        X = self.blocks[key]
        
        if self.type == 'cpu':
            return X
        else:
            return X.get()
    
    def hasTransposed(self):
        if self.type == 'gpu' and self.Xt is None:
            return False
        return True
    
    def set(self, X, key=None, col=None, row=None):
        if key is None:
            key = self.key
        self.blocks[key] = X
        self.X = self.blocks[key]
    
    def append(self, X, Xt=None, key=None):
        if key is None:
            raise Exception("Matrix: append requires key parameter")
        self.blocks[key] = X
        if Xt is not None:
            self.blocks_t[key] = Xt
    
    def shape(self):
        return self.X.shape

    def sum(self):
        return self.fetch().sum()
    
    def __add__(self, B):
        return self.X + B.get()
    
    def __sub__(self, B):
        return self.X - B.get()
    
    def __setitem__(self, key, value):
        self.blocks[key] = value
    
    def __getitem__(self, key):
        if key in self.blocks:
            return self.blocks[key]
        else:
            return None


class MockMatrix():
    def __init__(self, X, Xt=None):
        self.X = X
        self.Xt = Xt
    
    def __str__(self):
        return self.X