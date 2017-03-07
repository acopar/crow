
def run(inputs, outputs, config, dimensions, flags=None, sync=True, max_repeat=1):
    max_iter = config['max_iter']
    select_method = inputs['method']
    output = outputs['output']
    
    context = config['context']
    if context == 'gpu':
        from crow.context.gpucontext import GPUContext
        c = GPUContext(inputs, dimensions, config, test=flags['test'], dense=flags['dense'], sync=sync)
    elif context == 'cpu':
        from crow.context.cpucontext import CPUContext
        c = CPUContext(inputs, dimensions, config, test=flags['test'], dense=flags['dense'], sync=sync)
    else:
        raise Exception("Unrecognized context type %s" % context)
    
    clock_list = []
    info = None
    clock = None
    
    c.__enter__()
    c.dimensions['1'] = 1
    if flags['test'] == False:
        for i in range(max_repeat):
            if i > 0:
                c.load_gpu(data=False)
            if select_method == 'nmtf_long':
                c.run_nmtf_long(debug=flags['debug'], print_err=flags['error'])
            elif select_method == 'nmtf_long_err':
                c.run_nmtf_long_err(debug=flags['debug'], print_err=flags['error'])
            elif select_method == 'nmtf_ding':
                c.run_nmtf_ding(debug=flags['debug'], print_err=flags['error'])
            elif select_method == 'nmtf_ding_err':
                c.run_nmtf_ding_err(debug=flags['debug'], print_err=flags['error'])
            clock = None
            if 'main' in c.timer.t:
                clock = c.timer.t['main'] / (max_iter - 2)
            clock_list.append(clock)
    else:
        c.test_rules(debug=flags['debug'], print_err=flags['error'])
    
    c.exit()
    data = {'timer': c.timer.t, 'itertime': clock_list, 'rulefile': inputs['method'],
        'info': None, 'history': [], 'config': config}
    
    out = outputs['output']
    if out:
        c.save(out, outputs['results'], data)
    return data