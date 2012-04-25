#!/usr/bin/env python

from PIL import Image, ImageDraw, ImageFont
import struct
from random import randint
from hilbert import HilbertContainer

def ip_strtoint(ipstr):
    """Convert an IPv4 address in dotted-decimal to an integer."""
    return reduce(lambda x,y: (x<<8)+y,
            map(lambda x: int(x),
                ipstr.split('.', 4)))

def ip_inttostr(ip):
    """Convert an integer to an IPv4 address in dotted-decimal."""
    return '.'.join(map(lambda x: str(ord(x)), struct.pack('>L', ip)))

class IPMap(HilbertContainer):
    """Base class for IPMap objects. Puts IP/value pairs into buckets and generates
    a Hilbert curve mapping of buckets to x/y coordinates."""

    def __init__(self, cidr, side_length=16):
        """Required argument *cidr* is the network mask in CIDR notation, e.g. 192.168.1.0/24."""
        super(IPMap, self).__init__(side_length, empty=0)
        network, length = cidr.split('/', 1)
        numips = 2**(32 - int(length))
        self.mask = numips - 1
        self.network = ip_strtoint(network) & ~self.mask
        self.chunk = (1.0*numips) / (self.side_length ** 2) #ips per unit
        self.maxval = 0

    def xy2ip(self, x, y):
        """Given a set of x/y coordinates, return the lower bound of the IP
        addresses in the corresponding bucket."""
        return ip_inttostr(int(self.xy2d(x, y)*self.chunk) | self.network)

    def update_value(self, bucket, new):
        """Given a bucket, update its contents with the new value. Override this
        method to use a different algorithm than addition (the default)."""
        self[bucket] += new

    def bucket(self, ip):
        """Get the bucket (0..resolution] that the IP belongs in."""
        num = ip_strtoint(ip)
        if self.network != num & ~self.mask:
            raise RuntimeError, "IP outside network: %s, %d" % (ip, self.network)
        return int((num & self.mask)/self.chunk)

    def add(self, ip, value):
        """Update the IPMap with a new IP and value."""
        bucket = self.bucket(ip)
        self.update_value(bucket, value)
        self.maxval = max(self[bucket], self.maxval)

    def build(self):
        """Build and return the whole map. Assumes there are no more values to
        add, though the base class version is not destructive. Override this to
        generate different kinds of maps."""
        table = [[None for _ in range(0, self.side_length)] for _ in range(0, self.side_length)]
        for point, value in self:
            (x, y) = point
            table[x][y] = value
        return table

class IPMapHtmlTable(IPMap):
    """IPMap as an HTML table."""
    def get_class(self, num):
        """Override to enum classes."""
        return num

    def build(self, numclasses=10):
        """Returns the map as HTML *<tr>* and *<td>* elements, suitable for
        including in the *<tbody>* element of a table. Text content is the base
        IP for each bucket, and the class is the return value of
        self.get_class(self[bucket])."""
        depth_scale = self.maxval / (numclasses * 1.0)
        table = [[None for _ in range(0, self.side_length)] for _ in range(0, self.side_length)]
        for point, value in self:
            (x, y) = point
            table[x][y] = "<td class={classtag}>{ip}</td>".format(
                    classtag = self.get_class(value),
                    ip = self.xy2ip(x, y)
                    )
        return ''.join( map(lambda x: "<tr>{0}</tr>".format(''.join(x)), table) )

class IPMapImage(IPMap):
    """IPMap as a heatmap image."""
    palette = [
        53,  52,  61,    51,  51,  61,    49,  50,  62,    48,  48,  63,
        46,  46,  64,    44,  44,  65,    42,  42,  65,    40,  40,  67,
        37,  37,  67,    35,  35,  68,    32,  32,  69,    29,  29,  70,
        26,  26,  69,    24,  24,  71,    21,  21,  72,    19,  19,  73,
        16,  16,  74,    14,  14,  76,    12,  12,  77,    10,  10,  77,
        8,   8,   77,    7,   7,   79,    6,   6,   82,    5,   5,   85,
        4,   5,   89,    3,   4,   92,    2,   4,   97,    1,   5,   101,
        1,   6,   106,   1,   8,   110,   0,   9,   115,   0,   12,  120,
        0,   15,  126,   0,   18,  131,   0,   22,  136,   0,   26,  142,
        0,   30,  147,   0,   35,  152,   0,   40,  157,   0,   46,  162,
        0,   52,  167,   0,   58,  171,   0,   65,  175,   0,   71,  180,
        0,   78,  184,   0,   86,  189,   0,   93,  193,   0,   99,  196,
        0,   107, 199,   0,   112, 203,   0,   117, 205,   0,   122, 208,
        0,   130, 213,   0,   139, 218,   0,   147, 222,   0,   156, 228,
        0,   164, 232,   0,   173, 236,   0,   180, 240,   0,   188, 244,
        0,   195, 247,   0,   202, 250,   0,   208, 252,   0,   214, 254,
        0,   219, 255,   0,   224, 255,   0,   228, 255,   0,   232, 255,
        0,   234, 255,   0,   234, 254,   0,   234, 251,   0,   234, 248,
        0,   234, 246,   0,   234, 242,   0,   234, 238,   0,   234, 234,
        0,   234, 230,   0,   234, 225,   0,   234, 220,   0,   234, 214,
        0,   233, 209,   0,   231, 203,   0,   229, 197,   0,   227, 190,
        0,   224, 184,   0,   222, 178,   0,   219, 171,   0,   216, 165,
        0,   215, 160,   0,   213, 156,   0,   211, 151,   0,   209, 147,
        0,   207, 143,   0,   205, 138,   0,   203, 134,   0,   201, 129,
        0,   200, 125,   0,   198, 120,   0,   196, 116,   0,   194, 112,
        0,   193, 108,   0,   191, 104,   0,   190, 99,    0,   188, 95,
        0,   187, 92,    0,   186, 88,    0,   184, 84,    0,   184, 80,
        0,   183, 77,    0,   182, 74,    0,   182, 70,    0,   181, 68,
        0,   180, 65,    0,   180, 62,    0,   180, 60,    1,   180, 57,
        3,   180, 55,    6,   181, 53,    9,   181, 51,    12,  182, 48,
        15,  183, 46,    19,  184, 44,    23,  185, 43,    27,  187, 40,
        31,  188, 39,    36,  190, 37,    40,  191, 35,    45,  194, 34,
        50,  196, 33,    55,  198, 31,    60,  200, 30,    66,  202, 28,
        71,  204, 26,    76,  207, 25,    82,  209, 24,    88,  211, 23,
        93,  214, 22,    99,  216, 21,    105, 218, 20,    110, 221, 19,
        116, 223, 18,    122, 226, 17,    128, 228, 16,    134, 231, 15,
        140, 233, 14,    146, 236, 14,    151, 238, 13,    158, 240, 12,
        164, 242, 11,    169, 244, 11,    174, 246, 10,    180, 247, 9,
        185, 249, 9,     191, 251, 8,     197, 252, 8,     201, 252, 7,
        206, 252, 7,     211, 252, 6,     216, 252, 5,     220, 252, 5,
        225, 252, 4,     229, 252, 4,     233, 252, 3,     237, 252, 3,
        241, 252, 3,     244, 252, 2,     248, 252, 2,     250, 252, 1,
        253, 252, 0,     255, 251, 0,     255, 250, 0,     255, 247, 0,
        255, 245, 0,     255, 242, 0,     255, 238, 0,     255, 235, 0,
        255, 232, 0,     255, 227, 0,     255, 222, 0,     255, 218, 0,
        255, 213, 0,     255, 208, 0,     255, 203, 0,     255, 198, 0,
        255, 192, 0,     255, 187, 0,     255, 181, 0,     255, 175, 0,
        255, 169, 0,     255, 163, 0,     255, 156, 0,     255, 150, 0,
        255, 144, 0,     255, 137, 0,     255, 131, 0,     255, 124, 0,
        255, 118, 0,     255, 111, 0,     255, 105, 0,     255, 99,  0,
        255, 93,  0,     255, 86,  0,     255, 81,  0,     255, 74,  0,
        255, 68,  0,     255, 62,  0,     255, 57,  0,     255, 51,  0,
        255, 45,  0,     255, 41,  0,     255, 36,  0,     255, 31,  0,
        255, 26,  0,     255, 22,  0,     255, 18,  0,     255, 14,  0,
        255, 10,  0,     255, 6,   0,     255, 4,   0,     255, 1,   0,
        255, 0,   0,     255, 0,   0,     255, 0,   0,     255, 0,   0,
        255, 0,   0,     255, 0,   0,     255, 0,   0,     255, 0,   0,
        255, 1,   1,     255, 1,   1,     255, 2,   2,     255, 2,   2,
        255, 3,   3,     255, 5,   5,     255, 6,   6,     255, 8,   8,
        255, 11,  11,    255, 14,  14,    255, 18,  18,    255, 23,  23,
        255, 29,  29,    255, 37,  37,    255, 46,  46,    255, 56,  56,
        255, 67,  67,    255, 81,  81,    255, 94,  94,    255, 110, 110,
        255, 126, 126,   255, 142, 142,   255, 159, 159,   255, 176, 176,
        255, 193, 193,   255, 209, 209,   255, 224, 224,   255, 237, 237,
        ]
    def build(self, image_size=256, out="IPMap.png", fmt="PNG"):
        """Saves a square (*image_size* x *image_size*) image with values
        scaled to a 256-color heatmap."""
        depth_scale = self.maxval / (256.0)
        linear_scale = 1.0 * image_size / self.side_length
        img = Image.new('P', (image_size, image_size))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        for point, value in self:
            x, y = map(lambda x: x * linear_scale, point)
            ip_base = self.xy2ip(*point)
            draw.rectangle(
                    (x, y, x+linear_scale, y+linear_scale),
                    fill=int(value / depth_scale)
                    )
            draw.text((x, y), ip_base, font=font, fill=0)
        img.putpalette(IPMapImage.palette)
        img.save(out, fmt)


if __name__=='__main__':
    heatmap = IPMapImage("192.168.1.0/24", 8)
    for i in range(0,1000):
        heatmap.add('192.168.1.'+str(randint(0,255)), 10)
    heatmap.build()
