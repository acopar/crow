import numpy as np
from scipy.sparse import csr_matrix
from mpi4py import MPI

from crow.utils import *
from crow.interpreter.operations import *
from crow.transfer.cputransfer import *
from crow.functions.cpufunctions import *

from context import Context

import os
import psutil

class CPUOperation(Operation):
    def __init__(self, rank, rev_map, iblock_map, jblock_map, tblock_map, bigdot, kernel, dtype):
        super(CPUOperation,self).__init__(rank, rev_map, iblock_map, jblock_map, tblock_map, dtype)
            
        self.dot = dot
        self.bigdot = bigdot
        
        self.recv = cpu_recv
        self.send = cpu_send
        self.sync_only = sync_only
        self.empty_sync_matrix = empty_cpu_sync_matrix
        self.empty_mreduce = empty_cpu_reduce
        self.zeros_function = npzeros
        self.ones_function = npones
        self.number_function = npnumber
        self.czeros = npzeros
        self.load_kernel = load_kernel
        
        for name, func in FUNCTIONS.items():
            self.__dict__[name] = func
    
    def get_mem_info(self):
        pid = os.getpid()
        py = psutil.Process(pid)
        x = py.memory_info()
        memoryUse = py.memory_info()[0]/1024/1024
        return memoryUse

    def get_dynamic(self, matrix, transa='N', key=None):
        return matrix.get(transa=transa, key=key)

class CPUContext(Context):
    def __init__(self, inputs, dimensions, config, flags):
        comm = MPI.COMM_WORLD
        rank = comm.rank
        size = comm.size
        super(CPUContext,self).__init__(rank, size, inputs, dimensions, config, flags)
            
        _bigdot = bigdot
        if flags['dense'] == True:
            _bigdot = dot

        self.operation = CPUOperation(self.rank, self.rev_map, 
            self.iblock_map, self.jblock_map, self.tblock_map, _bigdot, kernel, self.dtype)
    
    def set_matrix(self, X, bid, key, dim):
        if key not in self.storage:
            model = self.models[key]
            self.storage[key] = Matrix(None, Xt=None, key=bid, model=model, cls='cpu')
        self.super_set_matrix(X, bid, key, dim)
    
    def new_matrix(self, bid, key, dim):
        if key not in self.storage:
            model = self.models[key]
            self.storage[key] = Matrix(None, Xt=None, key=bid, model=model, cls='cpu')
        self.super_new_matrix(bid, key, dim)
    
    def load_gpu(self, data=True):
        self.load(data=data)
    
    def __enter__(self):
        self.initial_memory = self.operation.get_mem_info()
        self.load_gpu()

    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type != None:
            print exc_type, exc_value, traceback
            import traceback as tb
            tb.print_tb(traceback)
            raise exc_value
        
        if self.test == True:
            return

    def exit(self):
        pass