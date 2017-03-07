import numpy as np
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


def divide(A, B, C):
    np.divide(A, (B + EPSILON), out=C)
    return C

def kernel_lin(A, B, C):
    C *= A / (B + EPSILON)
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
    D = np.multiply(A, B)
    return D

def sqrt(A, C):
    C = np.sqrt(A, C)
    return C

FUNCTIONS = {
    '_multiply': multiply,
    '_divide': divide,
    '_axis_sum': axis_sum,
    '_tr': transpose,
    '_add': add,
    '_sub': sub,
    '_sum': sum_all,
    'kernel': kernel,
    '_sqrt': sqrt
}