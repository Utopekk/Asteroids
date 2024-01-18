import time


class SpaceObject:
    def __init__(self, n_size, x, y, dx, dy, angle, vertices=None):
        self.n_size = n_size
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.angle = angle
        self.creation_time = time.time()
        self.vertices = vertices
