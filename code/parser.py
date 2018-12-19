from PIL import Image
from math import pi, cos, sin
from code import codec, generator

class Parser:
    def __init__(self, config):
        self.config = config
    
    def parse(self, file) -> list:
        image = Image.open(file)
        data = list(image.getdata())
        
        color = self.config.data_color
        center = (self.config.size / 2, self.config.size / 2)
        width = self.config.data_width / 2
        
        sw = self.config.size
        
        msg = []
        
        for i in range(1, 11):
            key = 'data_layer_' + str(i)
            try:
                layer = self.config.__getattr__(key)
                radius, count = layer
            except:
                continue
            
            point = (center[0], center[1])
            ac = 2 * pi / count
            field = (point[0] - radius, point[1] - radius,
                     point[0] + radius, point[1] + radius)
            i = 0
            dl = count
            
            lmsg = []
            while i < dl:
                angle = i * ac
                x, y = center[0] + cos(angle) * radius, center[1] - sin(angle) * radius
                x, y = int(x), int(y)
                
                pxl = data[Parser.coord(x, y, sw)]
                lmsg.append(Parser.colors_equal(color, pxl))
                i += 1
            
            if True not in lmsg:
                break
            
            msg += generator.Generator.apply_mask(lmsg, self.config.mask)
        
        
        return msg
        
    
    def force_parse(self, file) -> str:
        image = Image.open(file)
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
        if abs(width - height) > self.config.data_width:
            raise Exception('Cannot calculate image scaling')
        
        #if self.config.transform_key_radius is not None:
        
        
        
    
    def del_outline(data, size, color):
        
        stack = [(0, 0, False)]
        visited = [False for i in data]
        
        while len(stack) > 0:
            x, y, from_outline = stack[0]
            stack = stack[1:]
            
            if x < 0 or y < 0 or x >= size[0] or y >= size[1]:
                continue
            
            crd = Parser.coord(x, y, size[1])
            if visited[crd]: continue
            visited[crd] = True
            
            pxl = data[crd]
            if Parser.colors_equal(pxl, color):
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

        bounds = [size / 2 for i in range(4)]
        
        for x in range(size[0]):
            for j in range(size[1]):
                crd = Parser.coord(x, y)
                if not Parser.colors_equal(color, data[crd]):
                    continue
                
                bounds = [min(bounds[0], x),
                          min(bounds[1], y),
                          max(bounds[2], x),
                          max(bounds[3], y)]
                
        return bounds


    def coord(x, y, width):
        return x + y * width
        
    def colors_equal(c1, c2):
        return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2]) < 20
    
