from PIL import Image
from math import pi, cos, sin
from code import codec, generator

class Parser:
    def __init__(self, config):
        self.config = config
    
    def parse(self, file) -> list:
        image = Image.open(file)
        data = list(image.getdata())
        center = (self.config.size / 2, self.config.size / 2)
        
        index, radius, count = self.config.get_wider_layer()
        radius += self.config.data_width
        bounds = (center[0] - radius,
                  center[1] - radius,
                  center[0] + radius,
                  center[1] + radius)
        bounding = {'bounds': bounds,
                    'center': center,
                    'size': (radius * 2, radius * 2),
                    'scaling': (1,1)}
        
        return self._parse_impl(data, bounding)
        
    
    def force_parse(self, file) -> str:
        image = Image.open(file)
        
        mb = self.config.parser_raise_brightness
        if mb is not None and mb is not 1:
            image = raise_brightness(image, mb)
        
        data = list(image.getdata())
        
        # get rid of outline, if it is presented
        if self.config.outline_color is not None and self.config.outline_width is not None:
            color = self.config.outline_color
            data = Parser.del_outline(data, image.size, color)
            image.putdata(data)
        
        # calculating max radius where data is drawn
        data_radius = self.config.transform_key_radius
        if data_radius is None:
            data_radius = 0
        
        for i in range(1, 11):
            key = 'data_layer_' + str(i)
            try:
                data_radius = max(data_radius, self.config.__getattr__(key))
            except:
                pass
            
        # calculating bounds of data
        color = self.config.data_color
        bounds = Parser.get_data_bounds(data, image.size, color)
        
        # calculating scale of image
        width  = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]

        center = (bounds[0] + width / 2, bounds[1] + height / 2)
        
        index, radius, count = self.config.get_wider_layer()
        radius += self.config.data_width / 2
        bounding = {'bounds': bounds,
                    'center': center,
                    'size': (width, height),
                    'scaling': (width / radius / 2, height / radius / 2)}
        
        return self._parse_impl(data, bounding)
        
            
    def _parse_impl(self, data, bounding):
        
        color = self.config.data_color
        
        width = self.config.data_width / 2
        
        sw = self.config.size
        
        layers_data = []
        
        center = bounding['center']
        scaling = bounding['scaling']
        
        first_layer = True
        angle_offset = 0
        l = 1
        while l < 11:
            key = 'data_layer_' + str(l)
            try:
                layer = self.config.__getattr__(key)
                radius, count = layer
            except:
                l += 1
                continue
            
            ac = 2 * pi / count
            i = 0
            dl = count
            
            msg = []
            while i < dl:
                angle = i * ac + angle_offset
                x = center[0] + cos(angle) * radius * scaling[0]
                y = center[1] - sin(angle) * radius * scaling[1]
                x, y = int(x), int(y)
                
                pxl = data[coord(x, y, sw)]
                msg.append(colors_equal(color, pxl))
                i += 1
            
            if first_layer:
                prefix = [False] + [True] * 8 + [False]
                pos = find_sublist(msg, prefix)
                msg = msg[pos:] + msg[:pos]
                angle_offset = pos * ac
                first_layer = False
                
            if True not in msg:
                break
            
            layers_data.append(msg)
            l += 1
        
        if len(layers_data) == 0:
            raise Exception('Error while locating data, cannot find data of specified color')
        
        mask = layers_data[0][10:14]
        # clearing flags at first layer
        for i in range(14, len(layers_data[0])):
            if not layers_data[0][i]:
                break
            
        layers_data[0] = layers_data[0][i + 1:]

        msg = []
        for data in layers_data:
            msg += data

        # clearing garbage at last
        pos = find_sublist(msg, [True] * 8, start_at_end=True)
        if pos >= 0:
            msg = msg[0:pos]

        msg = generator.apply_mask(msg, mask)

        return msg
    
    
    def del_outline(data, size, color):
        
        stack = [(0, 0, False)]
        visited = [False for i in data]
        
        while len(stack) > 0:
            x, y, from_outline = stack[0]
            stack = stack[1:]
            
            if x < 0 or y < 0 or x >= size[0] or y >= size[1]:
                continue
            
            crd = coord(x, y, size[1])
            if visited[crd]: continue
            visited[crd] = True
            
            pxl = data[crd]
            if colors_equal(pxl, color):
                data[crd] = (0,0,0,0)
                from_outline = True
                
            elif not from_outline:
                from_outline = False
                
            else:
                continue
            
            stack.append((x, y-1, from_outline))
            stack.append((x, y+1, from_outline))
            stack.append((x-1, y, from_outline))
            stack.append((x+1, y, from_outline))
            
        return data
        
        
    def get_data_bounds(data, size, color):

        bounds = [size[i % 2] / 2 for i in range(4)]
        
        for x in range(size[0]):
            for y in range(size[1]):
                crd = coord(x, y, size[1])
                if not colors_equal(color, data[crd]):
                    continue
                
                bounds = [min(bounds[0], x),
                          min(bounds[1], y),
                          max(bounds[2], x),
                          max(bounds[3], y)]
                
        return bounds

    
def raise_brightness(image, value):

    source = image.split()
    
    Red = source[0].point(lambda i: i ** value)
    Green = source[1].point(lambda i: i ** value)
    Blue = source[2].point(lambda i: i ** value)

    return Image.merge(image.mode, (Red, Green, Blue, source[3]))


def coord(x, y, width):
    return x + y * width


def colors_equal(c1, c2):
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2]) < 20


def find_sublist(l, sl, start_at_end=False):
    count = 0
    if start_at_end:
        a, b, c = len(l)-1, 0, -1
    else:
        a, b, c = 0, len(l), 1
        
    for i in range(a, b, c):
        if l[i] == sl[count]:
            count += 1
            if count == len(sl):
                if start_at_end:
                    return i
                else:
                    return i - count + 1
        else:
            count = 0
    return -1
