import numpy as np

#dtype = np.float64
### Initialization procedures ###
def nprandom(x, y, seed=0, dtype=np.float32):
    np.random.seed(seed)
    X = np.random.rand(x, y)
    X = np.array(X, dtype=dtype, order='C')
    return X

def zeros(x, y, seed=0, dtype=np.float32):
    return np.array(np.zeros((x, y)), dtype=dtype, order='C')

def tri_initialize(d, seed=0, dtype=np.float32):
    np.random.seed(seed)
    U = np.random.rand(d['n'],d['k'])
    S = np.random.rand(d['k'],d['l'])
    V = np.random.rand(d['m'],d['l'])
    U = np.array(U, dtype=dtype, order='C')
    V = np.array(V, dtype=dtype, order='C')
    S = np.array(S, dtype=dtype, order='C')
    return U, S, V

def column_average(X, vertical='N', many=20):
    n = X.shape[0]
    m = X.shape[0]
    
    if vertical == 'N':
        a = np.zeros((n,1))
        for i in range(many):
            col = np.random.randint(n)
            a += X.getcol(col)
        a = a / many    
        
    else:
        a = np.zeros((1,m))
        for i in range(many):
            row = np.random.randint(m)
            a += X.getrow(row)
        a = a / many
    
    return a
    

def racol_initialize(X, d, seed=0):
    np.random.seed(seed)
    for i in range(d['k']):
        U[:,i] = column_average(X)
        V[:,i] = row_average.reshape(-1,1)
    
    S = np.random.rand(k,k)

