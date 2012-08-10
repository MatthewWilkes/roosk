def out():
    raw_map = open('mars.dat').readlines()
    width,height = map(int,raw_map.pop(0).split(','))
    pcols = set()
    from PIL import Image, ImageDraw
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


def inn():
    raw_map = open('mars.dat', "wb")
    from PIL import Image, ImageDraw
    im = Image.open(open("/Users/matthewwilkes/Desktop/mars.bmp","rb"))
    width,height = im.size
    raw_map.write("%d,%d\n" % (width, height))
    for y in range(height):
        for x in range(width):
          colour = im.getpixel((x,y))
          raw_map.write(''.join(map(chr, colour)) + '\n')