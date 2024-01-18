import math
from src.Settings import WIDTH, HEIGHT


class Utils:
    @staticmethod
    def rotate_vertices(vertices, angle):
        rotated_vertices = []
        for x, y in vertices:
            rotated_x = x * math.cos(angle) - y * math.sin(angle)
            rotated_y = x * math.sin(angle) + y * math.cos(angle)
            rotated_vertices.append((rotated_x, rotated_y))
        return rotated_vertices

    @staticmethod
    def wrap(ix, iy):
        ox, oy = ix, iy
        if ix < 0.0:
            ox = ix + WIDTH
        elif ix >= WIDTH:
            ox = ix - WIDTH
        if iy < 0.0:
            oy = iy + HEIGHT
        elif iy >= HEIGHT:
            oy = iy - HEIGHT
        return ox, oy
