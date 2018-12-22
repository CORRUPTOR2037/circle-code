def test(code):

    from code import codec, parser, generator, config_parser
    
    config = config_parser.Config()
    config.put('apply_mask', False)
    coder = codec.Codec(config)
    
    
    msg = [False] * 20 + [True] * 20 + [False] * 20

    gen = generator.Generator(config)
    gen.generate(msg)
        
    prs = parser.Parser(config)
    ret = prs.parse(config.generated_filename + '.png')
    
    assert len(msg) == len(ret)
    for i in range(len(msg)):
        assert msg[i] == ret[i]