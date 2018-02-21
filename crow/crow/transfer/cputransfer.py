import numpy as np

from mpi4py import MPI

EPSILON = 10**(-9)

comm = MPI.COMM_WORLD
#dtype = np.float64

def npzeros(n, m, dtype=np.float32):
    return np.array(np.zeros((n, m)), dtype=dtype, order='C')

def npzero_slices(slices, k, dtype=np.float32):
    return [npzeros(b-a,k, dtype=dtype) for a,b in slices]

def npones(n, m, dtype=np.float32):
    return np.array(np.ones((n, m)), dtype=dtype, order='C')

def npnumber(x, dtype=np.float32):
    return np.array(np.zeros((1,1))+x, dtype=dtype, order='C')

### Reducer and synchronizations ###

def sync_only():
    pass

def cpu_reduce(rank, device_list, output, source=0):
    if rank == source:
        kmp = None
        if len(device_list) > 0:
            kmp = npzeros(*output.shape, dtype=output.dtype)
        for b in device_list:
            cpu_recv(kmp, b)
            output += kmp
    else:
        cpu_send(output, source)

def cpu_sync_matrix(rank, device_list, output, source=0, collect=False):
    if rank == source:
        for b in device_list:
            cpu_send(output, b)
    else:
        cpu_recv(output, source)

def empty_cpu_reduce(rank, device_list, output, source=0):
    pass

def empty_cpu_sync_matrix(rank, device_list, output, source=0, collect=False):
    pass


### MPI calls ###

def dtype_to_mpi(t):
    if hasattr(MPI, '_typedict'):
        mpi_type = MPI._typedict[np.dtype(t).char]
    elif hasattr(MPI, '__TypeDict__'):
        mpi_type = MPI.__TypeDict__[np.dtype(t).char]
    else:
        raise ValueError('cannot convert type')
        return mpi_type

bufint_cpu = lambda arr: arr

def cpu_send(x_gpu, d):
    #print x_gpu.dtype, dtype_to_mpi(x_gpu.dtype)
    #return comm.Send(bufint_cpu(x_gpu), dest=d)
    return comm.Send([bufint_cpu(x_gpu), dtype_to_mpi(x_gpu.dtype)], dest=d)

def cpu_recv(x_gpu, d):
    #print x_gpu.dtype, dtype_to_mpi(x_gpu.dtype)
    #return comm.Recv(bufint_cpu(x_gpu), source=d)
    return comm.Recv([bufint_cpu(x_gpu), dtype_to_mpi(x_gpu.dtype)], source=d)

def cpu_isend(x_gpu, d):
    return comm.Isend([bufint_cpu(x_gpu), dtype_to_mpi(x_gpu.dtype)], dest=d)

def cpu_irecv(x_gpu, d):
    return comm.Irecv([bufint_cpu(x_gpu), dtype_to_mpi(x_gpu.dtype)], source=d)