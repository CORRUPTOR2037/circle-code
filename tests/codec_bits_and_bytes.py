def test(code):

    from code import codec
    
    a = [0,1,1,0,1,1,0,0, 1,1,0,1,0,1 ] # 108, 212
    b = codec.Codec.bits_to_bytes(a)
    
    assert b[0] == 108
    assert b[1] == 212
    
    c = codec.Codec.bytes_to_bits(b)
    
    a.append(0)
    a.append(0)

    assert c == a
