from SpaceObject import SpaceObject
import math
from utils import *


class Player(SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle, lives=3):
        super().__init__(n_size, x, y, dx, dy, angle)
        self.acceleration = 0.1
        self.speed = 10
        self.lives = lives
        self.destroyed = False

    def calculate_flame_vertices(self):
        flame_length = 40
        flame_width = 20
        flame_vertices = [
            (0, flame_length),
            (-flame_width / 2, 20),
            (flame_width / 2, 20)
        ]

        rotated_flame_vertices = Utils.rotate_vertices(flame_vertices, self.angle)

        translated_flame_vertices = [
            (x + self.x, y + self.y) for x, y in rotated_flame_vertices
        ]

        return translated_flame_vertices

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
