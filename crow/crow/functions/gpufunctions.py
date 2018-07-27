import numpy as np
import skcuda.linalg as linalg
import skcuda.misc
import pycuda.cumath
import pycuda.gpuarray
from cuda_cffi import cusparse

from crow.transfer.gputransfer import *
### Selective functions ###

def dot(A, B, C, transa='N', transb='N'):
    linalg.dot(A, B, out=C, transa=transa, transb=transb)
    return C

def bigsparse(X, B, C, transa='N', transb='N'):
    # TODO: transpose B
    #if transb == 'T':
    #    B = linalg.transpose(B)
    if transa == 'T':
        raise Exception("Transposing sparse matrix not supported")
    C = X.mm(B)
    return C

def load_kernel():
    X = gpuzeros(10,10)
    Y = gpuones(10,10)
    Z = gpuzeros(10,10)
    kernel(X, Y, Z)
    kernel_lin(X, Y, Z)
    X = gpuzeros(10, 10, dtype=np.float64)
    kernel(X, Y, Z)
    kernel_lin(X, Y, Z)

### Dynamic functions ###

def multiply(A, B, C):
    if type(A) == pycuda.gpuarray.GPUArray:
        return skcuda.misc.multiply(A, B)
    else:
        A_cpu = A.get()
        B_cpu = B.get()
        C = A_cpu.multiply(B_cpu)
        C = cusparse.CSR.to_CSR(C)
        return C

def divide_safe(A, B, C):
    if B.shape[0] == 1:
        D = np.divide(A.get(), B.get() + EPSILON)
        C = togpu(D, dtype=A.dtype)
    else:
        #C = skcuda.misc.divide(A, B)
        if A.dtype == np.float64:
            Dkern_div(A, B, C)
        kern_div(A, B, C)
    
    return C

def axis_sum(X, C, transa='N'):
    if transa == 'T':
        return skcuda.misc.sum(X, axis=1, out=C)
    else:
        return skcuda.misc.sum(X, axis=0, out=C)

def kernel(A, B, C, transa='N'):
    func = kern
    if A.dtype == np.float64:
        func = Dkern
    if transa == 'T':
        func(linalg.transpose(A), B, C)
    else:
        func(A, B, C)

def kernel_lin(A, B, C, transa='N'):
    func = kern_lin
    if A.dtype == np.float64:
        func = Dkern_lin
    if transa == 'T':
        func(linalg.transpose(A), B, C)
    else:
        func(A, B, C)

def transpose(A):
    return linalg.transpose(A)

def sub(A, B, C):
    return skcuda.misc.subtract(A, B)

def add(A, B, C):
    return skcuda.misc.add(A, B)

def sum_all(A, C):
    e = A.get().sum()
    C = C.get()
    C[0,0] = e
    C = togpu(C, dtype=A.dtype)
    return C

def sqrt(A, C):
    pycuda.cumath.sqrt(A, out=C)
    return C

def trace(A, C):
    trace = skcuda.linalg.trace(A)
    C = C.get()
    C[0,0] = trace
    C = togpu(C, dtype=A.dtype)
    return C

def project(A, C, transa='N'):
    MAXILON = 10**(9)
    A = A.get()
    A[np.where(A < 0)] = 0
    A[np.where(A > MAXILON)] = MAXILON
    return togpu(A, dtype=A.dtype)

def inverse(A, C):
    A = A.get()
    A = np.nan_to_num(A)
    try:
        X = la.inv(A)
        X = np.nan_to_num(X)
        return togpu(X, dtype=A.dtype)
    except la.LinAlgError:
        print("Warning: singular matrix")
        X = la.pinv(A)
        X = np.nan_to_num(X)
        return togpu(X, dtype=A.dtype)

def norm2(A, C):
    if type(A) == cusparse.CSR:
        Acpu = A.get()
        XX = Acpu.power(2)
        C = togpu(np.array(XX.sum()).reshape(1,1), dtype=A.dtype)
    else:
        XX = skcuda.misc.multiply(A, A).get()
        C = togpu(np.array(XX.sum()).reshape(1,1), dtype=A.dtype)
    return C

def _togpu(A):
    return togpu(A, dtype=A.dtype)

FUNCTIONS = {
    '_multiply': multiply,
    '_divide': divide_safe,
    '_axis_sum': axis_sum,
    '_tr': transpose,
    '_add': add,
    '_sub': sub,
    '_sum': sum_all,
    'kernel': kernel,
    'kernel_lin': kernel_lin,
    '_sqrt': sqrt,
    '_trace': trace,
    '_project': project,
    '_inverse': inverse,
    '_norm2': norm2,
    '_togpu': _togpu,
}