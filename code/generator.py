from PIL import Image, ImageDraw
import aggdraw

class Generator:
    def __init__(self, config):
        self.config = config
        
    
    def generate(self, text):
        image = Image.new('RGBA', self.config.size, (255,255,255,0))
        self.last_image = image
        #draw = ImageDraw.Draw(image)
        draw = aggdraw.Draw(image)
        
        self.draw_background(draw)
        
        self.insert_logo(image)
        
        self.insert_data()
        
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

        size = (width/2, width/2, self.config.size[0] - width/2, self.config.size[1] - width/2)

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
            
        draw.flush()
    
    
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
        
        ofs = [int((a - logo.size[i]) / 2) for i, a in enumerate(self.config.size)]
        
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
        
    
    def insert_data(self):
        pass
    
    
    def show(self):
        self.last_image.show()