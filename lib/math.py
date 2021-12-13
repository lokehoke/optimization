from math import sqrt

class Vector2(object):
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

def dist(v1, v2):
    return sqrt(float(v1.x - v2.x) * float(v1.x - v2.x) + float(v1.y - v2.y) * float(v1.y - v2.y))
