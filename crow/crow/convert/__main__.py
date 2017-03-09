#!/usr/bin/env python

import sys
import os
import time
import traceback
import subprocess
import argparse

from crow.convert.csv import *
from crow.utils import *

def to_csv(src, dst):
    check_file(src)
    X = load_numpy(src)
    write_csv(dst, X)

def to_numpy(src, dst):
    check_file(src)
    X = read_factor(src)
    save_numpy(dst, X)

def main():
    parser = argparse.ArgumentParser(version=VERSION, description='Crow')
    parser.add_argument("-c", "--csv", help="Convert numpy pickle to csv", action="store_true")
    parser.add_argument("-n", "--numpy", help="Convert csv to numpy", action="store_true")
    
    parser.add_argument('args', nargs='2', help='Two filenames in order: input output')
    args = parser.parse_args()
    
    if args.csv and args.numpy:
        raise Exception('Only one [-c, -n] can be selected at a time')
    
    argv = args.args
    if args.csv:
        src = argv[0]
        dst = argv[1]
        to_csv(src, dst)
    elif args.numpy:
        src = argv[0]
        dst = argv[1]
        to_numpy(src, dst)
    else:
        # guessing based on file extensions
        src = argv[0]
        dst = argv[1]
        src_ext = os.path.splitext(src)
        dst_ext = os.path.splitext(dst)
        if src_ext == '.csv' and dst_ext == '.npz':
            to_numpy(src, dst)
        elif src_ext == '.npz' and dst_ext == '.csv':
            to_csv(src, dst)
        elif src_ext == dst_ext:
            raise Exception("Both data types are the same, nothing to convert.")
            
        raise Exception("Unable to detect file types: currently only csv and npz types are available")
        
    
if __name__ == "__main__":
    main()
