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

def territory_id_to_colour(tid, is_marker=False):
    colour = [130, 120, 0]
    if is_marker:
        # this is where we print the id
        colour[2] = 255
    tid = str(tid)
    colour[0] += int(tid[0]) * 10
    colour[1] += int(tid[2]) * 20
    return tuple(colour)

def colour_to_territory_id(colour):
    return ((1+((colour[0]-128)/20))*100) + ((colour[1]-128)/10)

class ComplexMap(object):
    
    def __init__(self, filename):
        self.image = Image.open(open(filename, "rb"))

    def convert_to_dat(self, raw_map = None):
        if raw_map is None:
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
        return dict(enumerate(colours, start=1))

class ConvertedMap(ComplexMap):
    
    def __init__(self, simplemap):
        self.image = Image.new('RGB', simplemap.image.size)
        ImageDraw.floodfill(self.image, (0,0), (255,255,255))
        self.territories = set()
        draw = ImageDraw.Draw(self.image)
        territory_colours = simplemap.get_territories()
        inv_territory_colours = dict([(v,k) for (k,v) in territory_colours.items()])
        for fillpass in range(3):
            for x in xrange(self.image.size[0]):
                for y in xrange(self.image.size[1]):
                    colour = simplemap.image.getpixel((x,y))
                    if fillpass == 1 and colour in territory_colours.values():
                        tid = inv_territory_colours[colour] * 100
                        n_x, n_y = x, y
                        neighbours = [(x+1,y), (x,y+1), (x-1,y), (x,y-1)]
                        neighbours = [(x if x > 0 else self.image.size[0] - 1, y) for (x, y) in neighbours]
                        neighbours = [(x if x < self.image.size[0] else 0, y) for (x, y) in neighbours]
                        neighbours = [(x, y if y > 0 else self.image.size[1] - 1) for (x, y) in neighbours]
                        neighbours = [(x, y if y < self.image.size[1] else 0) for (x, y) in neighbours]
                        neighbours = set(self.image.getpixel(neighbour) for neighbour in neighbours)
                        neighbours = set(colour for colour in neighbours if colour[2] < 255 and colour != (0,0,0) and colour != (255,0,0))
                        if neighbours:
                            colour = max(neighbours)
                            tid = colour_to_territory_id(colour)
                        else:
                            tid = inv_territory_colours[colour] * 100
                            # generate a new tid
                            tid += 1
                            while (tid in self.territories):
                                tid += 1
                            self.territories.add(tid)
                            colour = territory_id_to_colour(tid)
                        x, y = n_x, n_y
                        ImageDraw.floodfill(self.image, (x,y), colour)
                    elif colour == (255, 255, 255):
                        if x < self.image.size[0]-1:
                            next_pixel = simplemap.image.getpixel((x+1,y))
                            if fillpass == 2 and (next_pixel in territory_colours.values()):
                                # We're not in the sea
                                tid = inv_territory_colours[next_pixel] * 100
                                draw.point((x,y), territory_id_to_colour(tid, is_marker=True))
                                continue
                        draw.point((x,y), colour)
                    elif colour in set([(0, 0, 0), (255, 0, 0)]):
                        draw.point((x,y), colour)

if __name__ == '__main__':
    import sys
    with open(sys.argv[2], "wb") as out:
        ConvertedMap(SimpleMap(sys.argv[1])).convert_to_dat(raw_map = out)