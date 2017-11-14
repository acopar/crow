import numpy as np
from scipy.sparse import *

from mpi4py import MPI
from pycuda import driver
import pycuda.gpuarray as gpuarray
import skcuda.linalg as linalg

from crow.utils import *
from crow.interpreter.operations import *
from crow.interpreter.matrix import *
from crow.functions.gpufunctions import *
from crow.transfer.cputransfer import npzeros
from crow.transfer.gputransfer import *
from cuda_cffi import cusparse

from context import Context

class GPUOperation(Operation):
    def __init__(self, rank, rev_map, iblock_map, jblock_map, tblock_map, bigdot, kernel):
        super(GPUOperation,self).__init__(rank, rev_map, iblock_map, jblock_map, tblock_map)

        self.dot = dot
        self.bigdot = bigdot
        
        self.recv = gpu_recv
        self.send = gpu_send
        self.sync_only = sync_only
        self.empty_sync_matrix = empty_gpu_sync_matrix
        self.empty_mreduce = empty_gpu_reduce
        self.zeros_function = gpuzeros
        self.ones_function = gpuones
        self.number_function = gpunumber
        self.czeros = npzeros
        self.load_kernel = load_kernel
        
        for name, func in FUNCTIONS.items():
            self.__dict__[name] = func

    def get_mem_info(self):
        (free,total) = driver.mem_get_info()
        x = float(free)
        y = float(total)
        
        return (y-x)/1024/1024
    
    def to_gpu(self, matrix, dense=True):
        for bid in matrix.blocks:
            matrix.type = 'gpu'
            if dense == False:
                matrix.blocks[bid] = cusparse.CSR.to_CSR(matrix.blocks[bid])
                matrix.blocks_t[bid] = cusparse.CSR.to_CSR(matrix.blocks[bid].T)
            else:
                matrix.blocks[bid] = togpu(matrix.blocks[bid])
    
    def from_gpu(self, matrix, dense=True):
        for bid in matrix.blocks:
            matrix.blocks[bid] = matrix.blocks[bid].get()
    
    def get_dynamic(self, matrix, transa='N', key=None):
        if matrix.swap == True:
            X = matrix.get(transa=transa, key=key)
            return togpu(X)
        else:
            return matrix.get(transa=transa, key=key)
        
    
class GPUContext(Context):
    def __init__(self, inputs, dimensions, config, flags):
        comm = MPI.COMM_WORLD
        rank = comm.rank
        size = comm.size
        super(GPUContext,self).__init__(rank, size, inputs, dimensions, config, flags)
        
        _bigdot = None
        if flags['dense'] == True:
            _bigdot = dot
        else:
            _bigdot = bigsparse
        
        self.dot = dot
        self.bigdot = bigsparse
        self.operation = GPUOperation(self.rank, self.rev_map, 
            self.iblock_map, self.jblock_map, self.tblock_map, _bigdot, kernel)
    
    def set_matrix(self, X, bid, key, dim):
        if key not in self.storage:
            model = self.models[key]
            self.storage[key] = Matrix(None, Xt=None, key=bid, model=model, cls='gpu')
        self.super_set_matrix(X, bid, key, dim)
    
    def new_matrix(self, bid, key, dim):
        if key not in self.storage:
            model = self.models[key]
            self.storage[key] = Matrix(None, Xt=None, key=bid, model=model, cls='gpu')
        self.super_new_matrix(bid, key, dim)
    
    def load_gpu(self, data=True):
        self.load(data=data)

        for m in self.storage:
            if m in self.data_vars and self.dense == False:
                self.operation.to_gpu(self.storage[m], dense=False)
            elif m in self.data_vars and self.lazy == True:
                self.storage[m].swap = True
                self.storage[m].type = 'cpu'
            else:
                self.operation.to_gpu(self.storage[m])
            
    def __enter__(self):
        self.load()
        
        ngpus = driver.Device.count()
        gpuid = self.rank % ngpus

        self.ctx  = driver.Device(gpuid).make_context()
        
        cusparse.init()
        linalg.init()

        self.initial_memory = self.operation.get_mem_info()
        #from crow.transfer.kernels import *
        #self.operation.mod = mod
        
        self.load_gpu()
    
    def exit(self):
        for m in self.storage:
            if m not in self.data_vars:
                matrix = self.storage[m]
                self.operation.from_gpu(matrix)
        self.ctx.detach()

    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type != None:
            print exc_type, exc_value, traceback
            import traceback as tb
            tb.print_tb(traceback)
            raise exc_value
        
        if self.test == True:
            return
        self.exit()
