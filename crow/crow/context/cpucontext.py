import numpy as np
from scipy.sparse import csr_matrix
from mpi4py import MPI

from crow.utils import *
from crow.interpreter.operations import *
from crow.transfer.cputransfer import *
from crow.functions.cpufunctions import *

from context import Context

class CPUOperation(Operation):
    def __init__(self, rank, rev_map, iblock_map, jblock_map, tblock_map, bigdot, kernel):
        super(CPUOperation,self).__init__(rank, rev_map, iblock_map, jblock_map, tblock_map)
            
        self.dot = dot
        self.bigdot = bigdot
        
        self.recv = cpu_recv
        self.send = cpu_send
        self.sync_only = sync_only
        self.empty_sync_matrix = empty_cpu_sync_matrix
        self.empty_mreduce = empty_cpu_reduce
        self.zeros_function = npzeros
        self.czeros = npzeros
        self.load_kernel = load_kernel
        
        for name, func in FUNCTIONS.items():
            self.__dict__[name] = func


class CPUContext(Context):
    def __init__(self, inputs, dimensions, config, dense=False, test=False, sync=True):
        comm = MPI.COMM_WORLD
        rank = comm.rank
        size = comm.size
        super(CPUContext,self).__init__(rank, size, inputs, dimensions, config, 
            dense=dense, test=test, sync=sync)
            
        _bigdot = bigdot
        if dense == True:
            _bigdot = dot

        self.operation = CPUOperation(self.rank, self.rev_map, 
            self.iblock_map, self.jblock_map, self.tblock_map, _bigdot, kernel)
    
    def load_gpu(self, data=True):
        self.load(data=data)
        matrix_storage = {}
        for m in self.storage:
            if type(self.storage[m]) == type({}):
                for bid in self.storage[m]:
                    data = self.storage[m][bid]
                    if m not in matrix_storage:
                        matrix_storage[m] = Matrix(data, key=bid, model=self.models[m])
                    else:
                        matrix_storage[m].append(data, key=bid)
            else:
                matrix_storage[m] = self.storage[m]
        self.storage = matrix_storage
    
    def __enter__(self):
        self.load_gpu()

    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type != None:
            print exc_type, exc_value, traceback
            import traceback as tb
            tb.print_tb(traceback)
            raise exc_value
        
        if self.test == True:
            return
        self.exit()
    
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
