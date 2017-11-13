import numpy as np
from scipy.sparse import *

from mpi4py import MPI
from pycuda import driver
import pycuda.gpuarray as gpuarray
import skcuda.linalg as linalg

from crow.utils import *
from crow.interpreter.operations import *
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
    
    def load_gpu(self, data=True):
        self.load(data=data)
        
        matrix_storage = {}
        
        for m in self.storage:
            if type(self.storage[m]) == type({}):
                for bid in self.storage[m]:
                    data = None
                    X = self.storage[m][bid]
                    if m in self.data_vars and self.dense == False:
                        Xg = cusparse.CSR.to_CSR(X)
                        Xtg = cusparse.CSR.to_CSR(X.T)
                        data = (Xg, Xtg)
                    else:
                        data = (togpu(X), None)
                    
                    if m not in matrix_storage:
                        matrix_storage[m] = Matrix(data[0], Xt=data[1], key=bid, model=self.models[m])
                    else:
                        matrix_storage[m].append(data[0], Xt=data[1], key=bid)
            else:
                matrix_storage[m] = self.storage[m]
        self.storage = matrix_storage
        
        #for m in self.storage:
        #    if m not in self.data_vars:
        #        M = self.storage[m][0]
        #        self.storage[m] = (togpu(M), None)
    
    
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
        cpu_storage = {}
        for m in self.storage:
            if m not in self.data_vars:
                matrix = self.storage[m]
                cpu_storage[m] = {}
                for bid in self.get_blocks():
                    #matrix.switch(bid)
                    cpu_storage[m][bid] = matrix.fetch(key=bid)
        self.storage = cpu_storage
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
