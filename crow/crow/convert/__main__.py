#!/usr/bin/env python

import sys
import os
import time
import traceback
import subprocess
import argparse

from crow.convert.csv import *
from crow.utils import *


def convert(src, dst, it, ot, header=False):
    check_file(src)
    X = None
    if it == 'coo':
        X = load_coo(src)
    elif it == 'csv':
        X = load_csv(src, delimiter=',')
        if header:
            X = X[1:]
        X = np.array(X, dtype=np.float32)
    elif it == 'tab':
        X = load_csv(src, delimiter='\t')
        if header:
            X = X[1:]
        X = np.array(X, dtype=np.float32)
    elif it == 'npz':
        X = load_numpy(src)
    elif it == 'pkl':
        X = load_file(src)

    if ot == 'coo':
        write_coo(dst, X)
    elif ot == 'csv':
        write_dense_csv(dst, X)
    elif ot == 'tab':
        write_dense_csv(dst, X, delimiter='\t')
    elif ot == 'npz':
        save_numpy(dst, X)
    elif ot == 'pkl':
        dump_file(dst, X)

def validate_filepath(src):
    cwd = os.getcwd()
    if cwd == '/home/crow':
        if check_file(src, soft=True) == False:
            print "Warning: Using paths relative to home inside the docker container"
            raise Exception("File not found at location %s/%s" % (cwd, src))
    else:
        check_file(src)
            

def main():
    parser = argparse.ArgumentParser(version=VERSION, description='Crow converter')
    parser.add_argument("-i", "--input", help="Explicitly set input type")
    parser.add_argument("-o", "--output", help="Explicitly set output type")
    parser.add_argument("--header", help="Skip header line", action="store_true")
    
    parser.add_argument('source', nargs=1, help='Two filenames in order: input output')
    parser.add_argument('target', nargs=1, help='Two filenames in order: input output')
    args = parser.parse_args()
    
    src = args.source[0]
    dst = args.target[0]
    
    validate_filepath(src)
    
    input_type = os.path.splitext(src)[1].replace('.', '')
    if args.input:
        input_type = args.input
    
    output_type = os.path.splitext(dst)[1].replace('.', '')
    if args.output:
        output_type = args.output
    
    supported_types = ['coo', 'csv', 'npz', 'pkl', 'tab']
    if input_type not in supported_types:
        raise Exception("Input type '%s' not supported" % input_type)
    
    if output_type not in supported_types:
        raise Exception("Output type '%s' not supported" % input_type)
    
    if input_type == output_type:
        raise Exception("Both data types are the same, nothing to do.")
    
    convert(src, dst, input_type, output_type, header=args.header)

        
    
if __name__ == "__main__":
    main()
