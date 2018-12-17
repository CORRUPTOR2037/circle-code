from reedsolo import RSCodec

class Codec:
    
    def __init__(self, config):
        
        alphabet = config.alphabet
        if config.alphabet is None:
            alphabet = ''
            for i in range(128):
                alphabet += chr(i)
        
        self.alphabet = alphabet
        self.size = 1
        while 2 ** self.size < len(self.alphabet):
            self.size += 1
        
        ecc = config.ecc if config.ecc is not None else 14
        self.codec = RSCodec(ecc) 
        
        
    def encode(self, message):
        bits = []
        for c in message:
            a = self.alphabet.find(c)
            if a < 0: continue
            
            for i in range(self.size):
                bits.append(a % 2)
                a = int(a / 2)
        
        encoded = self.codec.encode(Codec.bits_to_bytes(bits))
        encoded = Codec.bytes_to_bits(encoded)
        return encoded
    
    
    def decode(self, code):
        bits = self.codec.decode(code)
        msg = ''
        
        for i in range(0, len(bits), self.size):
            s = 0
            for j, c in enumerate(bits[i : i+self.size]):
                s += int(c) * (2 ** j)
            
            msg += chr(s)
            
        return msg

    
    def bits_to_bytes(bits_):
        bytes_ = []
        
        l = len(bits_)
        for i in range(0, l, 8):
            byte = 0
            for j in range(0, 8):
                if i + j < l:
                    byte = (byte << 1) | (1 if bits_[i + j] else 0)
                else:
                    byte = (byte << 1) | 0
            bytes_.append(byte)
            
        return bytes(bytes_)
    
    
    def bytes_to_bits(bytes_):
        bits_ = []
        
        for i in range(0, len(bytes_)):
            byte = bytes_[i]
            ar = []
            for j in range(0, 8):
                bit = byte % 2 == 1
                byte = byte >> 1
                ar.insert(0, bit)
            bits_ += ar
        
        return bits_


