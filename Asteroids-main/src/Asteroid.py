from SpaceObject import SpaceObject


class Asteroid(SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle, vertices):
        super().__init__(n_size, x, y, dx, dy, angle)
        self.vertices = vertices
