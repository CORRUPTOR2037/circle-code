def test(code):
    import os.path
    from code import config_parser
    
    path = os.path.join('resources', 'default.ini')
    config = config_parser.Config(path)
    