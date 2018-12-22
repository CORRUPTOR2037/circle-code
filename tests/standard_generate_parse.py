def test(code):

    from code import codec, parser, generator, config_parser
    
    config = config_parser.Config()
    coder = codec.Codec(config)
    
    msg = 'https://www.google.ru/images'
    encoded = coder.encode(msg)

    gen = generator.Generator(config)
    gen.generate(encoded)
        
    prs = parser.Parser(config)
    ret = prs.parse(config.generated_filename + '.png')
    ret = coder.decode(ret)
    
    assert msg == ret