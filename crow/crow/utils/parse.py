#!/usr/bin/env python

import os
from crow.utils.utils import to_path

def parse_x(b):
    if 'x' in b:
        x, y = b.split('x')
        x = int(x)
        y = int(y)
    else:
        y = 0
        x = int(b)
    return x, y

def parse_block(b):
    x, y = parse_x(b)
    if y == 0:
        y = 1
    return x, y

def parse_ks(b):
    x, y = parse_x(b)
    if y == 0:
        y = x
    return x, y

def from_arguments(arguments):
    dimensions = {}
    for x in arguments.split(','):
        if '=' not in x:
            raise Exception("Error parsing argument: %s" % x)
        a, b = x.split('=')
        if b.isdigit():
            dimensions[a] = int(b)
        elif isfloat(b):
            dimensions[a] = float(b)
        else:
            raise Exception("Unable to parse argument %s" % a)
    return dimensions


def get_data_folder(data_file):
    basename = os.path.basename(data_file)
    dirname = os.path.dirname(data_file)
    dataset = os.path.splitext(basename)[0]
    data_folder = to_path(dirname, dataset)
    return data_folder

def get_cache_folder(data_file, cache_folder):
    basename = os.path.basename(data_file)
    dirname = os.path.dirname(data_file)
    dataset = os.path.splitext(basename)[0]
    data_folder = to_path(cache_folder, dataset)
    return data_folder


def from_template(x, y):
    dct = {key: value for key, value in x.items()}
    for key in y:
        dct[key] = y[key]
    return dct