from crow.utils import *

def generate_blockmap(config, factor_folder, idx_file):
    nb = config['nb']
    mb = config['mb']
    parallel = config['parallel']
    block_map = {i: [] for i in range(parallel)}
    
    sfile = to_path(factor_folder, 'slices.pkl')
    slices, block_mask = load_file(sfile)
    
    iblock_map = {}
    jblock_map = {}
    tblock_map = {}
    blocks = []
    
    for i in range(nb):
        for j in range(mb):
            bid = (i,j)
            if block_mask[bid] == 1:
                continue
            
            rank = i*mb + j
            device = rank % parallel
            block_map[device].append(bid)
            blocks.append(bid)
    
    block_map_j = {i: [] for i in range(parallel)}
    for j in range(mb):
        for i in range(nb):
            bid = (i,j)
            if block_mask[bid] == 1:
                continue
            rank = i*mb + j
            device = rank % parallel
            block_map_j[device].append(bid)
    
    for i in range(nb):
        for j in range(mb):
            bid = (i,j)
            if block_mask[bid] == 1:
                continue
            iblock_map[(i,j)] = [b for b in blocks if b[0] == i and b != bid]
            jblock_map[(i,j)] = [b for b in blocks if b[1] == j and b != bid]
            tblock_map[(i,j)] = [b for b in blocks if b[0] == j and b[1] == i and b != bid]
    
    dump_file(idx_file, (block_map, block_map_j, iblock_map, jblock_map, tblock_map))