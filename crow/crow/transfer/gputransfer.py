import numpy as np

from pycuda import driver
import pycuda.gpuarray as gpuarray
from pycuda.elementwise import ElementwiseKernel
from mpi4py import MPI

EPSILON = 10**(-9)

comm = MPI.COMM_WORLD

### GPU convenience functions ###

def gpuzeros(n, m, slices=None):
    return gpuarray.zeros((n, m), dtype=np.float32, order='F')

def gpuzero_slices(slices, k):
    return [gpuzeros(b-a, k) for a,b in slices]

def gpuones(n, m):
    return togpu(np.ones((n,m)))

def gpuzeros_like(X):
    n, m = X.shape
    return gpuarray.zeros((n, m), dtype=np.float32, order='F')

def togpu(X):
    X = np.array(X, dtype=np.float32, order='F')
    return gpuarray.to_gpu(X)

def sync_only():
    sync_gpu(driver.Event())
    
def sync_gpu(event):
    event.record()
    event.synchronize()

def gpu_reduce(rank, device_list, output, source=0):
    if rank == source:
        kmp = None
        if len(device_list) > 0:
            kmp = gpuzeros(*output.shape)
        for b in device_list:
            gpu_recv(kmp, b)
            output += kmp
    else:
        sync_only()
        gpu_send(output, source)

def gpu_sync_matrix(rank, device_list, output, source=0, collect=False):
    if rank == source:
        if len(device_list) > 0:
            sync_only()
            for b in device_list:
                gpu_send(output, b)
    else:
        gpu_recv(output, source)

def empty_gpu_reduce(rank, device_list, output, source=0):
    sync_gpu(driver.Event())

def empty_gpu_sync_matrix(rank, device_list, output, source=0, collect=False):
    sync_gpu(driver.Event())

### CUDA kernels ###
code = """
z[i] = z[i] * sqrt(x[i] / (y[i] + 0.000000001));
if ( z[i] <  0.000000001 )
    z[i] =  0.000000001;
"""

code_lin = """
z[i] = z[i] * (x[i] / (y[i] + 0.000000001));
"""

code_div = """
z[i] = x[i] / (y[i] + 0.000001);
"""

kern = ElementwiseKernel(
        "float *x, float *y, float *z",
        code,
        "kern")

kern_lin = ElementwiseKernel(
        "float *x, float *y, float *z",
        code_lin,
        "kern_lin")

kern_div = ElementwiseKernel(
        "float *x, float *y, float *z",
        code_div,
        "kern_div")

### MPI calls ###

def dtype_to_mpi(t):
    if hasattr(MPI, '_typedict'):
        mpi_type = MPI._typedict[np.dtype(t).char]
    elif hasattr(MPI, '__TypeDict__'):
        mpi_type = MPI.__TypeDict__[np.dtype(t).char]
    else:
        raise ValueError('cannot convert type')
        return mpi_type

bufint_gpu = lambda arr: arr.gpudata.as_buffer(arr.nbytes)

def gpu_send(x_gpu, d):
    #print x_gpu.dtype
    #gpu_isend(x_gpu, d)
    #return comm.Send([bufint_gpu(x_gpu), dtype_to_mpi(x_gpu.dtype)], dest=d)
    return comm.Send(bufint_gpu(x_gpu), dest=d)

def gpu_recv(x_gpu, d):
    #pass
    #gpu_irecv(x_gpu, d)
    #return comm.Recv([bufint_gpu(x_gpu), dtype_to_mpi(x_gpu.dtype)], source=d)
    return comm.Recv(bufint_gpu(x_gpu), source=d)

def gpu_isend(x_gpu, d):
    return comm.Isend([bufint_gpu(x_gpu), dtype_to_mpi(x_gpu.dtype)], dest=d)

def gpu_irecv(x_gpu, d):
    return comm.Irecv([bufint_gpu(x_gpu), dtype_to_mpi(x_gpu.dtype)], source=d)
    
    
