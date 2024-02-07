import random
from Utils import Utils
from Particle import Particle
from Enemy import Enemy
from Asteroid import Asteroid
import math
from Settings import WIDTH, HEIGHT


class CreateManager:
    def __init__(self, player, vec_particles, vec_huge_asteroids, vec_small_asteroids, screen, stage):
        self.player = player
        self.vec_particles = vec_particles
        self.vec_huge_asteroids = vec_huge_asteroids
        self.vec_small_asteroids = vec_small_asteroids
        self.screen = screen
        self.stage = stage
        self.enemy = None

    def create_particle_effect(self, x, y, color, num_particles):
        for _ in range(num_particles):

            lifetime = random.uniform(0.2, 0.5)
            dx = random.uniform(-50, 50)
            dy = random.uniform(-50, 50)
            particle = Particle(x, y, color, lifetime, dx, dy)
            self.vec_particles.append(particle)

    def create_enemy(self):
        x = random.uniform(0, 0)
        y = random.uniform(0, 0)
        while (
                self.player.x + 150 < x < self.player.x - 150 or
                self.player.y + 150 < y < self.player.y - 150
        ):
            x = random.uniform(0, 0)
            y = random.uniform(0, 0)

        self.enemy = Enemy(screen=self.screen, x=x, y=y, dx=0, dy=0, angle=0)

    def create_random_asteroids(self, num_asteroids, size_range, is_huge=True):
        asteroids = self.vec_huge_asteroids if is_huge else self.vec_small_asteroids

        for _ in range(num_asteroids):
            size = random.randint(*size_range)
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            while math.fabs(self.player.x - x) <= 400 and math.fabs(self.player.y - y) <= 400:
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)

            vertices = Utils.generate_irregular_shape(size)
            asteroids.append(Asteroid(
                n_size=size,
                x=x,
                y=y,
                dx=random.uniform(-10, 10),
                dy=random.uniform(-10, 10),
                angle=random.uniform(0, 2 * math.pi),
                vertices=vertices
            ))

    def create_random_huge_asteroids(self, num_asteroids):
        self.create_random_asteroids(num_asteroids,
                                     (50 + self.stage.asteroidDifficultySize, 80 + self.stage.asteroidDifficultySize),
                                     is_huge=True)
