def test(code):

    from code import codec, config_parser


    c = codec.Codec(config_parser.Config())
    
    a = 'Hello, world'
    b = c.encode(a)
    
    assert a == c.decode(b)
    
    
    c.set_alphabet('0123456789')
    
    a = '72435'
    b = c.encode(a)

    assert a == c.decode(b)
    

