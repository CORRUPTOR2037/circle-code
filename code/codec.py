from reedsolo import RSCodec

class Codec:

    def __init__(self, config):
        
        self.set_alphabet(config.alphabet)
        
        self.ecc = config.ecc if config.ecc is not None else 14
        self.codec = RSCodec(self.ecc)
        
    
    def set_alphabet(self, text):
        
        if text is None:
            text = ''
            for i in range(1, 128):
                text += chr(i)
            
        self.alphabet = text
        self.size = 1
        while 2 ** self.size < len(self.alphabet) + 1:
            self.size += 1
    
    
    def encode(self, message):
        
        bits = []
        
        for c in message:
            a = self.alphabet.find(c)
            if a < 0: continue
            
            for i in range(self.size):
                bits.append(a % 2)
                a = int(a / 2)
        
        
        encoded = Codec.bits_to_bytes(bits)
        encoded = self.codec.encode(encoded)
        encoded = Codec.bytes_to_bits(encoded)
        
        return encoded
    
    
    def decode(self, decoded):
        decoded = Codec.bits_to_bytes(decoded)
        while decoded[-1] == 0:
            decoded = decoded[:-1]
        
        decoded = self.codec.decode(decoded)
        
        bits = Codec.bytes_to_bits(decoded)
        msg = ''
            
        for i in range(0, len(bits), self.size):

            s = 0
            for j, c in enumerate(bits[i : i+self.size]):
                c = int(c) * (2 ** j)
                s += c
            
            if s == 0:
                break
            msg += self.alphabet[s]
        
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

