import random
import math
from Utils import Utils
from Particle import Particle
from Asteroid import Asteroid
from Enemy import Enemy
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

    def create_enemy(self):
        start_positions = ["top_left", "top_right", "bottom_left", "bottom_right"]
        start_position = random.choice(start_positions)
        self.enemy = Enemy(screen=self.screen, start_position=start_position, shooting_interval=3.0)
        return self.enemy
    