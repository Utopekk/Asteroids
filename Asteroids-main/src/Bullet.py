from SpaceObject import SpaceObject


class Bullet(SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle, acceleration):
        super().__init__(n_size, x, y, dx, dy, angle)
        self.acceleration = acceleration
