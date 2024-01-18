from SpaceObject import SpaceObject
import math

class Asteroid(SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle, vertices):
        super().__init__(n_size, x, y, dx, dy, angle)
        self.vertices = vertices

    def rotate_vertices(self, angle):
        rotated_vertices = []
        for x, y in self.vertices:
            rotated_x = x * math.cos(angle) - y * math.sin(angle)
            rotated_y = x * math.sin(angle) + y * math.cos(angle)
            rotated_vertices.append((rotated_x, rotated_y))
        return rotated_vertices
