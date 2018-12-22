from PIL import Image, ImageDraw
import aggdraw
from math import cos, sin, pi
from code import codec

class Generator:
    def __init__(self, config):
        self.config = config
        
    
    def generate(self, data):
        image = Image.new('RGBA', (self.config.size, self.config.size), (255,255,255,0))
        self.last_image = image

        #draw = ImageDraw.Draw(image)
        draw = aggdraw.Draw(image)
        
        self.draw_background(draw)
        draw.flush()
        
        self.insert_logo(image)
        draw = aggdraw.Draw(image)
        
        if self.config.transform_key_radius is not None:
            self.insert_transform_key(draw)
        
        if data is not None:
            self.insert_data(draw, data)
        else:
            self.test_layers(draw)
        
        draw.flush()
        
        image.save(self.config.generated_filename + '.png', 'PNG')
        pass
    
    
    def draw_background(self, draw):
        shape = self.config.background_shape
        
        if shape not in ['circle', 'rectangle', 'soft_rectangle']:
            raise Exception('Unknown background shape type:', shape)
        
        if self.config.background_color is not None:
            fill = aggdraw.Brush(self.config.background_color)
        else:
            return
            
        if self.config.outline_width is not None and self.config.outline_color is not None:
            outline = aggdraw.Pen(self.config.outline_color, self.config.outline_width)
            width = self.config.outline_width
        else:
            outline = None
            width = 0

        size = (width/2, width/2, self.config.size - width/2, self.config.size - width/2)

        if shape == 'circle':
            draw.ellipse(size, outline, fill)
            
        elif shape == 'rectangle':
            draw.rectangle(size, outline, fill)
            
        elif shape == 'soft_rectangle':
            ratio = self.config.background_shape_circle_ratio
            if ratio is None:
                ratio = 8
            
            round_width = (size[2] / ratio, size[3] / ratio)
            round_half = (round_width[0] * 2, round_width[1] * 2)
            
            # Cross
            draw.rectangle((round_width[0], size[1], size[2] - round_width[0], size[3]),
                           None, fill)
            draw.rectangle((size[0], round_width[1], size[2], size[3] - round_width[1]),
                           None, fill)
            
            # Border circles
            draw.ellipse((size[0], size[1], round_half[0], round_half[1]),
                           None, fill)
            draw.ellipse((size[2] - round_half[0], size[1], size[2], round_half[1]),
                           None, fill)
            draw.ellipse((size[0], size[3] - round_half[1], round_half[0], size[3]),
                           None, fill)
            draw.ellipse((size[2] - round_half[0], size[3] - round_half[1], size[2], size[3]),
                           None, fill)
            
            # Outline
            draw.line((round_width[0], size[1], size[2] - round_width[0], size[1]), outline)
            draw.line((round_width[0], size[3], size[2] - round_width[0], size[3]), outline)
            draw.line((size[0], round_width[1], size[0], size[3] - round_width[1]), outline)
            draw.line((size[2], round_width[1], size[2], size[3] - round_width[1]), outline)
            draw.arc((size[0], size[1], round_half[0], round_half[1]), 90, 180, outline)
            draw.arc((size[2] - round_half[0], size[1], size[2], round_half[1]), 0, 90, outline)
            draw.arc((size[0], size[3] - round_half[1], round_half[0], size[3]), 180, 270, outline)
            draw.arc((size[2] - round_half[0], size[3] - round_half[1], size[2], size[3]), 270, 360, outline)

    
    def insert_logo(self, image):
        draw_type = self.config.logo_draw_type
        logo_path = self.config.logo_path
        
        if logo_path is None:
            return
        
        if draw_type not in ['set', 'sub']:
            raise Exception('Unknown logo drawing type:', draw_type)
        
        data = list(image.getdata())
        logo = Image.open(logo_path)
        logo = logo.resize((int(logo.size[0] * self.config.logo_scale),
                     int(logo.size[1] * self.config.logo_scale)))
        
        if logo.size[0] > image.size[0] or logo.size[1] > image.size[1]:
            raise Exception('Logo is larger than image code.')
        
        ofs = [int((self.config.size - a) / 2) for i, a in enumerate(logo.size)]
        
        def to_rgba(c):
            if len(c) <= 4: return c
            c = list(c)
            for i in range(len(c),4):
                c.append(255)
            return tuple(c)
        
        if draw_type == 'set':
            def add(src, dst):
                src, dst = to_rgba(src), to_rgba(dst)
                c = [int(src[i] * src[3]/255 + dst[i] * (255 - src[3])/255) for i in range(3)]
                c.append(min(src[3] + dst[3], 255))
                return tuple(c)

        if draw_type == 'sub':
            _data_color = to_rgba(self.config.data_color)
            def add(src, dst):
                src, dst = to_rgba(src), to_rgba(dst)
                c = [int(_data_color[i] * src[3]/255 + dst[i] * (255 - src[3])/255) for i in range(3)]
                c.append(min(src[3] + dst[3], 255))
                return tuple(c)
        
        for j in range(logo.size[1]):
            for i in range(logo.size[0]):
                coord = (j + ofs[1]) * image.size[1] + i + ofs[0]
                data[coord] = add(logo.getpixel((i, j)), data[coord])
        
        image.putdata(data)
        
                
    def insert_data(self, draw, data):
        center = (self.config.size / 2, self.config.size / 2)
        width = self.config.data_width / 2
        fill = aggdraw.Brush(self.config.data_color)
        pen = aggdraw.Pen(self.config.data_color, width * 2 + 1)
        
        index, radius, count = self.config.get_lower_layer()
        
        mask, trigger_pos = find_best_mask(data)
        prefix = [False] + [True] * 8 + [False] + mask
        if trigger_pos is not None:
            trigger_pos = count - trigger_pos
            while trigger_pos > 0:
                trigger_pos -= 1
                prefix.append(True)
        
        prefix.append(False)
        data = prefix + apply_mask(data, mask)
        data_size = len(data)
        
        ofs = 0
        random_generator = yield_random()
        for i in range(1, 11):
            key = 'data_layer_' + str(i)
            try:
                layer = self.config.__getattr__(key)
                radius, count = layer
            except:
                continue
            
            layer_data = data[ofs : min(data_size, ofs+count)]
            ofs += count
            
            if ofs > data_size:
                # if data has ended on this layer
                if len(layer_data) > 0:
                    layer_data += [True] * 8
                while len(layer_data) < count:
                    layer_data.append(next(random_generator))
            
            print(layer_data)
            Generator.draw_layer(draw, center, radius, count, layer_data, width, fill, pen)
            
        if ofs < data_size:
            raise Exception('Not enough layers to encode data on. Data width:', data_size, ', Can be encoded:', ofs)
    
    
    def draw_layer(draw, center, radius, density, data, width, fill, pen):
        ac, ar = 2 * pi / density, 360 / density
        field = (center[0] - radius, center[1] - radius,
                 center[0] + radius, center[1] + radius)
        
        i1 = 0
        data_size = min(density, len(data))
        while i1 < data_size:
            if not data[i1]:
                i1 += 1
                continue
                
            i2 = i1
            while data[(i2 + 1) % data_size]:
                i2 += 1
                
            p1 = (i1) * ar
            a1 = (i1) * ac
            a1 = (center[0] + cos(a1) * radius, center[1] - sin(a1) * radius)
            p2 = (i2) * ar
            a2 = (i2) * ac
            a2 = (center[0] + cos(a2) * radius, center[1] - sin(a2) * radius)

            draw.ellipse((a1[0] - width, a1[1] - width,
                          a1[0] + width, a1[1] + width), None, fill)
            draw.ellipse((a2[0] - width, a2[1] - width,
                          a2[0] + width, a2[1] + width), None, fill)
            draw.arc(field, p1, p2, pen)
            i1 = i2 + 1
        
        
    def test_layers(self, draw):
        center = (self.config.size / 2, self.config.size / 2)
        width = self.config.data_width / 2
        fill = aggdraw.Brush(self.config.data_color)

        for i in range(1, 11):
            try:
                key = 'data_layer_' + str(i)
                layer = self.config.__getattr__(key)
                radius, count = layer
                Generator.test_layer(draw, center, radius, count, width, fill)
            except:
                continue
        
        
    def test_layer(draw, center, radius, density, width, fill):
        ac, ar = 2 * pi / density, 360 / density
        field = (center[0] - radius, center[1] - radius,
                 center[0] + radius, center[1] + radius)
        
        i1 = 0
        while i1 < density:
            p1 = (i1) * ar
            a1 = (i1) * ac
            a1 = (center[0] + cos(a1) * radius, center[1] - sin(a1) * radius)
            draw.ellipse((a1[0] - width, a1[1] - width,
                          a1[0] + width, a1[1] + width), None, fill)
            i1 += 1
         
    
    def show(self):
        self.last_image.show()
    
    
def to_byte(number):
    ar = []
    
    for i in range(8):
        ar.append(number % 2 == 1)
        number = number >> 1
    
    return ar
       
       
def apply_mask(data, mask):       
    l = len(mask)
    return [not d if mask[i % l] else d for i, d in enumerate(data)]


def find_best_mask(data):
    m = (0,0)
    for i in range(1, 16):
        mask = to_byte(i)[0:4]
        ndata = apply_mask(data, mask)
        count = 0
        for j, bit in enumerate(ndata):
            if bit == True:
                count += 1
            else:
                count = 0
            if count == 8:
                if j > m[1]:
                    m = (mask, j)
                break
        if count < 8:
            return (mask, None)
    return m


import random
def yield_random():
    past = [False] * 7
    while True:
        if False not in past:
            nxt = False
        elif True not in past:
            nxt = True
        else:
            nxt = random.randint(0, 1) == 1
            
        del past[0]
        past.append(nxt)
        yield nxt
