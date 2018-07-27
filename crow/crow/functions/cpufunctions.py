import numpy as np
import scipy.linalg as la
from scipy.sparse import csr_matrix
from crow.transfer.cputransfer import *

### Selective functions ###

def dot(A, B, C, transa='N', transb='N'):
    if transa == 'T':
        A = A.T
    if transb == 'T':
        B = B.T
    np.dot(A, B, out=C)
    return C


def bigdot(X, B, C, transa='N', transb='N'):
    if transa == 'T':
        raise Exception("Transposing sparse matrix not supported")
    D = X.dot(B)
    return np.asarray(D)

def load_kernel():
    pass

### Dynamic functions ###

def kernel(A, B, C, transa='N'):
    if transa == 'T':
        C *= np.sqrt(A.T / (B + EPSILON))
    else:
        C *= np.sqrt(A / (B + EPSILON))
    C[C<EPSILON] = EPSILON
    return C


#def divide(A, B, C):
#    np.divide(A, (B + EPSILON), out=C)
#    return C

def divide(A, B, C):
    EPSILON = 10**(-9)
    if np.isscalar(B):
        if B < EPSILON:
            B = EPSILON
    else:
        B[np.where(B < EPSILON)] = EPSILON
    np.divide(A, B, out=C)
    return C

def kernel_lin(A, B, C, transa='N'):
    if transa == 'T':
        C *= (A.T / (B + EPSILON))
    else:
        C *= (A / (B + EPSILON))
    C[C<EPSILON] = EPSILON
    return C

def axis_sum(X, C, transa='N'):
    if transa == 'T':
        return np.sum(X, axis=1).reshape(1,-1)
    else:
        return np.sum(X, axis=0).reshape(1,-1)

def transpose(X):
    return X.T

def sub(A, B, C):
    np.subtract(A, B, C)
    return C

def add(A, B, C):
    np.add(A, B, C)
    return C

def sum_all(A, C):
    C[0,0] = np.sum(A)
    return C

def multiply(A, B, C):
    if type(A) == np.ndarray:
        D = np.multiply(A, B)
    else:
        D = A.multiply(B)
    return D

def sqrt(A, C):
    C = np.sqrt(A, C)
    return C

def trace(A, C):
    C = np.trace(A)
    return C

def project(A, C, transa='N'):
    MAXILON = 10**(9)
    A[np.where(A < 0)] = 0
    A[np.where(A > MAXILON)] = MAXILON
    return A


def inverse(A, C):
    A = np.nan_to_num(A)
    try:
        X = la.inv(A)
        X = np.nan_to_num(X)
        return X
    except la.LinAlgError:
        print("Warning: singular matrix")
        X = la.pinv(A)
        X = np.nan_to_num(X)
        return X

def norm2(A, C):
    if type(A) == csr_matrix:
        XX = A.power(2)
        C[0,0] = XX.sum()
    else:
        XX = np.multiply(A, A)
        C[0,0] = np.sum(XX)
    return C

def _togpu(A):
    return A

FUNCTIONS = {
    '_multiply': multiply,
    '_divide': divide,
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