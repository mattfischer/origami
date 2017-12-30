import math

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return 'geo.Point(%s, %s)' % (self.x, self.y)

    def __eq__(self, other):
        if other is None:
            return False
        return self.x == other.x and self.y == other.y

    def __add__(self, vector):
        return Point(self.x + vector.x, self.y + vector.y)

    def __sub__(self, other):
        if isinstance(other, Point):
            return Vector(self.x - other.x, self.y - other.y)
        else:
            return Point(self.x - other.x, self.y - other.y)

class Vector(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return 'geo.Vector(%s, %s)' % (self.x, self.y)

    def __eq__(self, other):
        if other is None:
            return False
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        else:
            return Vector(self.x * other, self.y * other)

    def __div__(self, other):
        return Vector(self.x / other, self.y / other)

    def __truediv__(self, other):
        return self.__div__(other)

    def __neg__(self):
        return self * -1

    def magnitude2(self):
        return self * self

    def magnitude(self):
        return math.sqrt(self.magnitude2())

    def normalize(self):
        return self / self.magnitude()

class Line(object):
    def __init__(self, normal, offset):
        self.normal = normal
        self.offset = offset

    def __repr__(self):
        return 'geo.Line(%s, %s)' % (self.normal, self.offset)

    def __eq__(self, other):
        if other is None:
            return False
        return self.normal == other.normal and self.offset == other.offset

class Segment(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __repr__(self):
        return 'geo.Segment(%s, %s)' % (self.start, self.end)

    def __eq__(self, other):
        if other is None:
            return False
        return self.start == other.start and self.end == other.end

    def points(self):
        return [self.start, self.end]

    def line(self):
        v = self.end - self.start
        normal = Vector(v.y, -v.x).normalize()
        offset = (self.start - Point(0, 0)) * normal
        return Line(normal, offset)

    def length(self):
        return (self.end - self.start).magnitude()

    def length2(self):
        return (self.end - self.start).magnitude2()