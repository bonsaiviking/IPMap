
def xy2d(side_length, x, y):
    """ Find the distance of the point (x, y) along a Hilbert curve
    which fills a square *side_length* units on a side. """
    s = side_length / 2
    d = 0
    while( s > 0 ):
        rx = 1 if (x & s) else 0
        ry = 1 if (y & s) else 0
        d += s * s * ((3 * rx) ^ ry)
        if (ry == 0):
            if (rx == 1):
                x = s-1 - x
                y = s-1 - y
            (x, y) = (y, x)
        s /= 2
    return d

def d2xy(side_length, d):
    """ Find the coordinates (x, y) of a point some distance *d* along
    a Hilbert curve which fills a square *side_length* units on a side. """
    x = y = 0
    s = 1
    while( s < side_length ):
        rx = 1 & (d/2)
        ry = 1 & (d ^ rx)
        if (ry == 0):
            if (rx == 1):
                x = s-1 - x
                y = s-1 - y
            (x, y) = (y, x)
        x += s * rx
        y += s * ry
        d /= 4
        s *= 2
    return x, y

class HilbertCurve(object):
    def __init__(self, side_length):
        self.side_length = int(side_length)

    def d2xy(self, d):
        if d >= self.side_length ** 2:
            raise IndexError, "distance out of range"
        return d2xy(self.side_length, d)

    def xy2d(self, x, y):
        if x >= self.side_length or y >= self.side_length:
            raise IndexError, "coordinates out of range"
        return xy2d(self.side_length, x, y)

class HilbertContainer(HilbertCurve):
    def __init__(self, side_length, empty=None):
        super(HilbertContainer, self).__init__(side_length)
        self.d = [empty for _ in range(0, self.side_length ** 2)]

    def __getitem__(self, d):
        if hasattr(d, '__len__'):
            return self.d[self.xy2d(*d)]
        else:
            return self.d[d]
    
    def __setitem__(self, d, value):
        if hasattr(d, '__len__'):
            self.d[self.xy2d(*d)] = value
        else:
            self.d[d] = value
    
    def __iter__(self):
        """ Generator for iterating over the curve. Yields a 2-tuple of (x, y)
        and the value at that point, in Hilbert-curve order (a la turtle) """
        for d in xrange(0,self.side_length ** 2):
            yield ( self.d2xy(d), self.d[d] )

