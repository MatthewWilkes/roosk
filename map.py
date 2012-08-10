from PIL import Image, ImageDraw
from cStringIO import StringIO

def out():
    raw_map = open('mars.dat').readlines()
    width,height = map(int,raw_map.pop(0).split(','))
    pcols = set()
    size = width,height
    im = Image.new('RGB', size)
    draw = ImageDraw.Draw(im)
    for y in range(height):
      row = []
      offset = width*y
      x = 0
      for point in raw_map[offset:offset+width]:
          colour = tuple(map(ord,point))
          pcols.add(colour)
          row.append('.' if colour[1] else ' ')
          draw.point((x,y), colour[:3])
          x+=1
      print ''.join(row)
    im.show()

class ComplexMap(object):
    
    def __init__(self, filename):
        self.image = Image.open(open(filename, "rb"))

    def convert_to_dat(self):
        raw_map = StringIO()
        width,height = self.image.size
        raw_map.write("%d,%d\n" % (width, height))
        for y in range(height):
            for x in range(width):
              colour = self.image.getpixel((x,y))
              raw_map.write(''.join(map(chr, colour)) + '\n')
        return raw_map

class SimpleMap(object):
    
    def __init__(self, filename):
        self.image = Image.open(open(filename, "rb"))

    def get_unique_colours(self):
        colours = set()
        width,height = self.image.size
        for y in range(height):
            for x in range(width):
              colours.add(self.image.getpixel((x,y)))
        return colours

    def get_territories(self):
        colours = self.get_unique_colours()
        colours.remove((0, 0, 0)) # borders
        colours.remove((255, 255, 255)) # water
        colours.remove((255, 0, 0)) # bridges
        return enumerate(colours)

if __name__ == '__main__':
    print dict(SimpleMap("/Users/matthewwilkes/Desktop/mars.bmp").get_territories())