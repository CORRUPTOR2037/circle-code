def test(tests_path, code_package):
    import sys
    sys.path.insert(0, tests_path)
    
    from os import listdir
    from os.path import isfile, join
    from importlib import import_module
    import traceback
    
    files = [f for f in listdir(tests_path) if isfile(join(tests_path, f))]
    
    for file in files:
        if file[-3:] != '.py':
            continue
        file = file[0:-3]
        try:
            test_module = import_module(file)
            if not hasattr(test_module, 'test'):
                raise Exception('Test function is not found')
        except:
            traceback.print_exc()
            continue
        
        try:
            test_module.test(code_package)
            print('Test', file, 'passed')
        except:
            print('Test', file, 'failed')
            traceback.print_exc()
