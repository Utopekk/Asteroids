from SpaceObject import SpaceObject
import math


class Player(SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle, lives=3):
        super().__init__(n_size, x, y, dx, dy, angle)
        self.acceleration = 0.1
        self.speed = 10
        self.lives = lives

    def calculate_vertices(self, mx, my):
        vertices = []
        for i in range(3):
            vertices.append((
                mx[i] * math.cos(self.angle) - my[i] * math.sin(self.angle) + self.x,
                mx[i] * math.sin(self.angle) + my[i] * math.cos(self.angle) + self.y
            ))
        return vertices

    def calculate_firing_position(self):
        mx = [0.0, -16.0, 16.0]
        my = [-35.2, 16.0, 16.0]
        return self.calculate_vertices(mx, my)
