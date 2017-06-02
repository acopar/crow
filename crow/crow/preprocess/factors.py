from crow.preprocess import initialize
from crow.utils import *

def measure_data(folder, config, label=None):
    nb = config['nb']
    mb = config['mb']
    balanced = True
    if config['imbalanced']:
        balanced = False
    dense = True
    if config['sparse']:
        dense = False
    
    N, M = 0, 0
    shapes = {}
    isizes = [0]
    jsizes = [0]
    mask = {}
    iavail = {}
    javail = {}
    
    for i in range(nb):
        for j in range(mb):
            filename = to_path(folder, '%d_%d' % (nb, mb), '%d_%d.npz' % (i, j))
            if dense == False:
                if balanced == True: 
                    filename = to_path(folder, '%d_%d' % (nb, mb), 's%d_%d.npz' % (i, j))
                else:
                    filename = to_path(folder, '%d_%d' % (nb, mb), 'i%d_%d.npz' % (i, j))
            if not os.path.isfile(filename):
                print 'Warning: Dataset file not found: %s' % filename
                mask[(i,j)] = 1
                continue
            data = load_numpy(filename)
            X_cpu = data
            n, m = X_cpu.shape
            if X_cpu.dtype != np.float32:
                raise Exception("Error: Data type must be float32")
            
            if i not in iavail:
                N += n
                isizes.append(n + isizes[-1])
                iavail[i] = m
            
            if j not in javail:
                M += m
                jsizes.append(m + jsizes[-1])
                javail[j]  = n
            
            shapes['%d_%d' % (i, j)] = (n, m)
            mask[(i,j)] = 0
    
    islices = [(isizes[i], isizes[i+1]) for i in range(nb)]
    jslices = [(jsizes[i], jsizes[i+1]) for i in range(mb)]
    
    shape = (N, M)
    slices = islices, jslices
    return shape, slices, mask

def data_analyze(cache_folder, factor_folder, config, dimensions, matrices):
    init = config['init']
    block_mask = {}
    data = False
    slices = None
    X = None
    for d in matrices:
        key = d['name']
        dim = d['size']
        type_ = d['type']
        if type_ == 'data':
            if data == True:
                raise Exception("Multiple datasets not supported")
            
            shape, slices, mask = measure_data(cache_folder, config, label=key)
            for k in mask:
                block_mask[k] = mask[k]
            dimensions[dim[0]] = shape[0]
            if dim[0] == dim[1]:
                print 'Symmetric dataset'
                if shape[0] != shape[1]:
                    raise Exception("Error: asymmetric dataset in symmetric method")
            else:
                dimensions[dim[1]] = shape[1]
            data = True
            
            if init == 'vcol':
                filename = to_path(cache_folder, '%d_%d' % (1, 1), '%d_%d.npz' % (0, 0))
                if not os.path.isfile(filename):
                    print 'Warning: Dataset file not found: %s' % filename
                    mask[(i,j)] = 1
                    continue
                X = load_numpy(filename)
    
    sfile = to_path(factor_folder, 'slices.pkl')
    dump_file(sfile, (slices, block_mask))
    return X

def generate_factors(factor_folder, config, dimensions, matrices, X):
    init = config['init']
    seed = config['seed']
    storage = {}
    
    for d in matrices:
        key = d['name']
        dim = d['size']
        type_ = d['type']
        if type_ == 'factor':
            if dim[0] not in dimensions:
                raise Exception("Undefined parameter %s" % dim[0])
            if dim[1] not in dimensions:
                raise Exception("Undefined parameter %s" % dim[1])
            shp = dimensions[dim[0]], dimensions[dim[1]]
            shp0 = shp
            shp = (int(shp[0]), int(shp[1]))
            
            if init == 'random':
                storage[key] = initialize.nprandom(shp[0], shp[1], seed=seed)
            elif init == 'zeros':
                storage[key] = initialize.zeros(shp[0], shp[1])
            elif init == 'vcol':
                if dim[0] == 'n' and dim[1] in ['k', 'l']:
                    storage[key] = initialize.racol_initialize(X, shp, axis=1, seed=seed)
                elif dim[0] == 'm' and dim[1] in ['k', 'l']:
                    storage[key] = initialize.racol_initialize(X, shp, axis=0, seed=seed)
                elif dim[0] in ['k', 'l'] and dim[1] in ['k', 'l']:
                    storage[key] = initialize.nprandom(shp[0], shp[1], seed=seed)
                else:
                    raise Exception("Unsupported vcol dimensions", dim)
    
    ffile = to_path(factor_folder, 'factors.pkl')
    dump_file(ffile, (dimensions, storage))

def block_shape_labels(matrices):
    nkey = None
    mkey = None
    
    for d in matrices:
        key = d['name']
        dim = d['size']
        typ = d['type']
        if typ == 'data':
            nkey = dim[0]
            mkey = dim[1]

    if nkey == None or mkey == None:
        raise Exception("Data dimensions undefined %sx%s" % (nkey, mkey))
    
    return nkey, mkey

def partition_factors(factor_folder, factor_cache, config, dimensions, matrices):
    nb = config['nb']
    mb = config['mb']
    ffile = to_path(factor_folder, 'factors.pkl')
    sfile = to_path(factor_folder, 'slices.pkl')
    dimensions, storage = load_file(ffile)
    slices, block_mask = load_file(sfile)
    
    nkey, mkey = block_shape_labels(matrices)
    
    islices, jslices = slices
    
    for d in matrices:
        key = d['name']
        dim = d['size']
        typ = d['type']
        if typ == 'factor':
            if dim[0] == nkey:
                storage[key] = [storage[key][a:b,:] for a,b in islices]
            elif dim[0] == mkey:
                storage[key] = [storage[key][a:b,:] for a,b in jslices]
    
    for i in range(nb):
        for j in range(mb):
            block_factors = {}
            for d in matrices:
                key = d['name']
                dim = d['size']
                typ = d['type']
                if typ == 'factor':
                    if dim[0] == nkey:
                        block_factors[key] = storage[key][i] 
                    elif dim[0] == mkey:
                        block_factors[key] = storage[key][j]
                    else:
                        block_factors[key] = storage[key]
            fblock_file = to_path(factor_cache,  '%d_%d.pkl' % (i, j))
            dump_file(fblock_file, block_factors)

    
