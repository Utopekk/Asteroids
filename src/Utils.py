import math
from Settings import WIDTH, HEIGHT
import random
import pygame
from Asteroid import Asteroid


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

    @staticmethod
    def generate_irregular_shape(size):
        num_vertices = random.randint(5, 10)
        angle_increment = 2 * math.pi / num_vertices
        vertices = []
        for i in range(num_vertices):
            radius = size + random.uniform(-size / 2, size / 2)
            x = radius * math.cos(i * angle_increment)
            y = radius * math.sin(i * angle_increment)
            vertices.append((x, y))
        return vertices

    @staticmethod
    def get_rotated_rect(vertices, angle, x, y):
        rotated_vertices = Utils.rotate_vertices(vertices, angle)
        min_x = min(x for x, y in rotated_vertices)
        min_y = min(y for x, y in rotated_vertices)
        max_x = max(x for x, y in rotated_vertices)
        max_y = max(y for x, y in rotated_vertices)
        return pygame.Rect(min_x + x, min_y + y, max_x - min_x, max_y - min_y)

    @staticmethod
    def med_asteroids(asteroid):
        medium_asteroids = Asteroid(
            n_size=random.randint(20, 30),
            x=asteroid.x + random.uniform(-10, 10),
            y=asteroid.y + random.uniform(-10, 10),
            dx=random.uniform(-25, 25),
            dy=random.uniform(-25, 25),
            angle=random.uniform(0, 2 * math.pi),
            vertices=Utils.generate_irregular_shape(random.randint(28, 35))
        )
        return medium_asteroids

    @staticmethod
    def sma_asteroids(asteroid):
        small_asteroids = Asteroid(
            n_size=random.randint(12, 20),
            x=asteroid.x + random.uniform(-10, 10),
            y=asteroid.y + random.uniform(-10, 10),
            dx=random.uniform(-25, 25),
            dy=random.uniform(-25, 25),
            angle=random.uniform(0, 2 * math.pi),
            vertices=Utils.generate_irregular_shape(random.randint(15, 20))
        )
        return small_asteroids

    @staticmethod
    def remove_asteroid(asteroid, vec_medium_asteroids, vec_small_asteroids):
        vec_medium_asteroids.remove(asteroid)
        small_asteroid_1 = Utils.sma_asteroids(asteroid)
        small_asteroid_2 = Utils.sma_asteroids(asteroid)
        vec_small_asteroids.extend([small_asteroid_1, small_asteroid_2])
