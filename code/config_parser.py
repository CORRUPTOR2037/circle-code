import codecs

class Config:
    
    def __init__(self, file = None, encoding='UTF-8'):
        
        self.generate()
        if file is None:
            return
        
        try:
            file = codecs.open(file, 'r', encoding)
            self.parse_lines(file.readlines())
        
        except Exception as e:
            print(str(e) + '. Using default values')


    def generate(self):
        self.config = {
            'logo_path': 'resources/logo.png',
            'logo_draw_type': 'sub', # set, sub,
            'logo_scale': 1,
            'size': (512, 512),
            'background_shape': 'circle',  # circle, rectangle, soft_rectangle
            'background_color': (121, 180, 110),
            'outline_color': None,
            'outline_width': None,
            'data_color': (255, 255, 255),
            'generated_filename': 'code'
        }


    def parse_lines(self, lines):
        def num(s):
            if '.' in s:
                return float(s)
            return int(s)
        
        for line in lines:
            line = line.split('#')[0].strip()
            if len(line) == 0:
                continue
            
            line = line.split('=')
            key = line[0].strip()
            val = line[1].strip()

            if len(val) > 0 and val[0] == '(':
                val = val.replace(' ', '')
                val = tuple(val[1:-1].split(','))
                try:
                    val = tuple([num(a) for a in val])
                except:
                    pass
            elif len(val) == 0:
                val = None
            else:
                try:
                    val = num(val)
                except Exception as e:
                    pass
            
            self.config[key] = val
    
    def __getattr__(self, name):
        return self.config[name] if name in self.config else None
    
    def __repr__(self):
        return self.config.__repr__()
