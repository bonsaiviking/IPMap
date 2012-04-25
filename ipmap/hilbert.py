import math

def xy2d(side_length, x, y):
    """Find the distance of the point (x, y) along a Hilbert curve
    which fills a square *side_length* units on a side."""
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
    """Find the coordinates (x, y) of a point some distance *d* along
    a Hilbert curve which fills a square *side_length* units on a side."""
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
    """Object-oriented interface to 2-dimensional Hilbert curves.
    
    A HilbertCurve object has one attribute, *side_length*, which is the square of
    the order of the curve. A third-order Hilbert curve has a side length of 2**3, or 8.
    The side length will be coerced into the next highest positive power of 2.
    """
    def __init__(self, side_length):
        self.side_length = side_length

    @property
    def side_length(self):
        return self._side_length

    @side_length.setter
    def side_length(self, l):
        if l <= 0:
            self._side_length = 1
        else:
            self._side_length = 2**int(math.ceil(math.log(l, 2)))

    def d2xy(self, d):
        """Find the coordinates (x, y) of a point some distance *d* along the curve."""
        if d >= self.side_length ** 2:
            raise IndexError, "distance out of range"
        return d2xy(self.side_length, d)

    def xy2d(self, x, y):
        """Find the distance of the point (x, y) along the curve."""
        if x >= self.side_length or y >= self.side_length:
            raise IndexError, "coordinates out of range"
        return xy2d(self.side_length, x, y)

class HilbertContainer(HilbertCurve):
    """A container that can be indexed along either the 1- or 2-dimensional aspects
    of a Hilbert curve.
    
    Indexing by the 1-dimensional distance is done just like indexing into a list: curve[d]
    
    Indexing by 2-dimensional coordinates works the same way: curve[x,y]
    
    For example:
    
    >>> curve = HilbertContainer(8)
    >>> curve[3] = "example"
    >>> curve.d2xy(3)
    (1, 0)
    >>> curve[1,0]
    'example'
    """
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
        """Generator for iterating over the curve. Yields a 2-tuple of (x, y)
        and the value at that point, in Hilbert-curve order (a la turtle)."""
        for d in xrange(0,self.side_length ** 2):
            yield ( self.d2xy(d), self.d[d] )

