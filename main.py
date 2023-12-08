import pygame
import sys
import math
import time
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


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


class Player(SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle):
        super().__init__(n_size, x, y, dx, dy, angle)
        self.acceleration = 0.1
        self.speed = 10
        self.score = 0

    def calculate_vertices(self, mx, my):
        vertices = []
        for i in range(3):
            vertices.append((
                mx[i] * math.cos(self.angle) - my[i] * math.sin(self.angle) + self.x,
                mx[i] * math.sin(self.angle) + my[i] * math.cos(self.angle) + self.y
            ))
        return vertices

    def calculate_firing_position(self):
        mx = [0.0, -20.0, 20.0]
        my = [-44.0, 20.0, 20.0]
        return self.calculate_vertices(mx, my)


class Asteroid(SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle, vertices):
        super().__init__(n_size, x, y, dx, dy, angle)
        self.vertices = vertices


class Bullet(SpaceObject):
    def __init__(self, n_size, x, y, dx, dy, angle, acceleration):
        super().__init__(n_size, x, y, dx, dy, angle)
        self.acceleration = acceleration


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


def rotate_vertices(vertices, angle):
    rotated_vertices = []
    for x, y in vertices:
        rotated_x = x * math.cos(angle) - y * math.sin(angle)
        rotated_y = x * math.sin(angle) + y * math.cos(angle)
        rotated_vertices.append((rotated_x, rotated_y))
    return rotated_vertices


class AsteroidsGame:
    def __init__(self, screen_width, screen_height):
        self.elapsed_time = None
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Asteroids")
        self.vec_huge_asteroids = []
        self.vec_small_asteroids = []
        self.player = Player(n_size=20.0, x=screen_width / 2.0, y=screen_height / 2.0, dx=0.0, dy=0.0, angle=0.0)
        self.vec_bullets = []
        self.interval_shooting = 1
        self.last_time_shot = 0
        self.counter_shooting = 0
        self.game_over = False
        self.game_over_time = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.player.angle -= 1.2 * self.elapsed_time

        if keys[pygame.K_RIGHT]:
            self.player.angle += 1.2 * self.elapsed_time

        if keys[pygame.K_UP]:
            acceleration = 20.0 * self.player.acceleration
            self.player.dx += math.sin(self.player.angle) * acceleration
            self.player.dy += -math.cos(self.player.angle) * acceleration

            # Calculate the new speed
            self.player.speed = math.sqrt(self.player.dx ** 2 + self.player.dy ** 2)

            # Limit the speed
            max_speed = 140.0  # km/min
            if self.player.speed > max_speed:
                scale_factor = max_speed / self.player.speed
                self.player.dx *= scale_factor
                self.player.dy *= scale_factor

        elif not (self.player.speed <= 10):
            damping_factor = 0.98
            self.player.dx *= damping_factor
            self.player.dy *= damping_factor
            self.player.speed = math.sqrt(self.player.dx ** 2 + self.player.dy ** 2)

        firing_position = self.player.calculate_firing_position()
        now = int(time.time())
        if keys[pygame.K_SPACE] and (now - self.last_time_shot) >= self.interval_shooting:
            self.vec_bullets.append(Bullet(
                n_size=0,
                x=firing_position[0][0],
                y=firing_position[0][1],
                dx=50.0 * math.sin(self.player.angle),
                dy=-50.0 * math.cos(self.player.angle),
                angle=0.0,
                acceleration=1 + self.player.speed * 0.007
            ))
            self.last_time_shot = now
            self.counter_shooting += 1

    def update_objects(self):
        self.vec_bullets = [b for b in self.vec_bullets if time.time() - b.creation_time <= 1.5]

        for bullet in self.vec_bullets:
            bullet.x += bullet.dx * self.elapsed_time * bullet.acceleration
            bullet.y += bullet.dy * self.elapsed_time * bullet.acceleration
            bullet.x, bullet.y = self.wrap(bullet.x, bullet.y)

        for asteroid in self.vec_huge_asteroids:
            asteroid.x += asteroid.dx * self.elapsed_time
            asteroid.y += asteroid.dy * self.elapsed_time
            asteroid.x, asteroid.y = self.wrap(asteroid.x, asteroid.y)

        for asteroid in self.vec_small_asteroids:
            asteroid.x += asteroid.dx * self.elapsed_time
            asteroid.y += asteroid.dy * self.elapsed_time
            asteroid.x, asteroid.y = self.wrap(asteroid.x, asteroid.y)

        self.player.x += self.player.dx * self.elapsed_time
        self.player.y += self.player.dy * self.elapsed_time
        self.player.x, self.player.y = self.wrap(self.player.x, self.player.y)

    def draw_objects(self):
        self.draw_asteroids()
        for bullet in self.vec_bullets:
            bullet.x += bullet.dx * self.elapsed_time * bullet.acceleration
            bullet.y += bullet.dy * self.elapsed_time * bullet.acceleration
            bullet.x, bullet.y = self.wrap(bullet.x, bullet.y)
            pygame.draw.rect(self.screen, WHITE, pygame.Rect(bullet.x, bullet.y, 5, 5))

        self.draw_player_ship()

    def wrap(self, ix, iy):
        ox, oy = ix, iy
        if ix < 0.0:
            ox = ix + self.screen_width
        elif ix >= self.screen_width:
            ox = ix - self.screen_width
        if iy < 0.0:
            oy = iy + self.screen_height
        elif iy >= self.screen_height:
            oy = iy - self.screen_height
        return ox, oy

    def create_random_asteroids(self, num_asteroids, size_range, is_huge=True):
        asteroids = self.vec_huge_asteroids if is_huge else self.vec_small_asteroids

        for _ in range(num_asteroids):
            size = random.randint(*size_range)
            x = random.uniform(-self.screen_width, self.screen_width)
            y = random.uniform(-self.screen_height, self.screen_height)

            # Ensure asteroids are not created too close to the player
            while (
                    self.player.x + 250 < x < self.player.x - 250 or
                    self.player.y + 250 < y < self.player.y - 250
            ):
                x = random.uniform(-self.screen_width, self.screen_width)
                y = random.uniform(-self.screen_width, self.screen_width)

            vertices = generate_irregular_shape(size)
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
        self.create_random_asteroids(num_asteroids, (36, 52), is_huge=True)

    def create_random_small_asteroids(self, num_asteroids):
        self.create_random_asteroids(num_asteroids, (15, 26), is_huge=False)

    def draw_asteroids(self):
        for asteroid in self.vec_huge_asteroids:
            rotated_vertices = rotate_vertices(asteroid.vertices, asteroid.angle)
            translated_vertices = [(x + asteroid.x, y + asteroid.y) for x, y in rotated_vertices]
            pygame.draw.polygon(self.screen, WHITE, translated_vertices)
        for asteroid in self.vec_small_asteroids:
            rotated_vertices = rotate_vertices(asteroid.vertices, asteroid.angle)
            translated_vertices = [(x + asteroid.x, y + asteroid.y) for x, y in rotated_vertices]
            pygame.draw.polygon(self.screen, WHITE, translated_vertices)

    def draw_player_ship(self):
        vertices = self.player.calculate_firing_position()
        pygame.draw.polygon(self.screen, RED, vertices)

    def check_collisions(self):
        if self.game_over:
            return

        # Create a bounding box (hitbox) around the rotated and translated vertices of the player
        player_rotated_vertices = rotate_vertices([(0, -24), (-10, 10), (10, 10)], self.player.angle)
        min_x_player = min(x for x, y in player_rotated_vertices)
        min_y_player = min(y for x, y in player_rotated_vertices)
        max_x_player = max(x for x, y in player_rotated_vertices)
        max_y_player = max(y for x, y in player_rotated_vertices)
        player_rect = pygame.Rect(min_x_player + self.player.x, min_y_player + self.player.y,
                                  max_x_player - min_x_player, max_y_player - min_y_player)

        for asteroid in self.vec_huge_asteroids:
            # Create a bounding box (hitbox) around the rotated and translated vertices of the asteroid
            rotated_vertices = rotate_vertices(asteroid.vertices, asteroid.angle)
            min_x = min(x for x, y in rotated_vertices)
            min_y = min(y for x, y in rotated_vertices)
            max_x = max(x for x, y in rotated_vertices)
            max_y = max(y for x, y in rotated_vertices)
            asteroid_rect = pygame.Rect(min_x + asteroid.x, min_y + asteroid.y, max_x - min_x, max_y - min_y)

            # Check collision between player and asteroid hitbox
            if player_rect.colliderect(asteroid_rect):
                print("Game Over")
                self.game_over = True
                self.game_over_time = time.time()

            # Check collision between bullets and asteroid hitbox
            for bullet in self.vec_bullets[:]:
                bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)
                if asteroid_rect.colliderect(bullet_rect):
                    self.vec_bullets.remove(bullet)
                    self.vec_huge_asteroids.remove(asteroid)

                    # Divide the huge asteroid into two small asteroids
                    x = asteroid.x
                    y = asteroid.y
                    self.vec_small_asteroids.append(Asteroid(
                        n_size=random.randint(15, 26),
                        x=x + random.uniform(-10, 10),
                        y=y + random.uniform(-10, 10),
                        dx=random.uniform(-10, 10),
                        dy=random.uniform(-10, 10),
                        angle=random.uniform(0, 2 * math.pi),
                        vertices=generate_irregular_shape(random.randint(15, 26))
                    ))
                    self.vec_small_asteroids.append(Asteroid(
                        n_size=random.randint(15, 26),
                        x=x + random.uniform(-10, 10),
                        y=y + random.uniform(-10, 10),
                        dx=random.uniform(-10, 10),
                        dy=random.uniform(-10, 10),
                        angle=random.uniform(0, 2 * math.pi),
                        vertices=generate_irregular_shape(random.randint(15, 26))
                    ))
                    self.player.score += 100
        for asteroid in self.vec_small_asteroids[:]:
            # Create a bounding box (hitbox) around the rotated and translated vertices of the asteroid
            rotated_vertices = rotate_vertices(asteroid.vertices, asteroid.angle)
            min_x = min(x for x, y in rotated_vertices)
            min_y = min(y for x, y in rotated_vertices)
            max_x = max(x for x, y in rotated_vertices)
            max_y = max(y for x, y in rotated_vertices)
            asteroid_rect = pygame.Rect(min_x + asteroid.x, min_y + asteroid.y, max_x - min_x, max_y - min_y)

            # Check collision between player and asteroid hitbox
            if player_rect.colliderect(asteroid_rect):
                print("Game Over")
                self.game_over = True
                self.game_over_time = time.time()

            # Check collision between bullets and asteroid hitbox
            for bullet in self.vec_bullets[:]:
                bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)
                if asteroid_rect.colliderect(bullet_rect):
                    self.vec_bullets.remove(bullet)
                    self.vec_small_asteroids.remove(asteroid)
                    self.player.score += 50
                    self.create_random_huge_asteroids(num_asteroids=1)

    def run_game(self):
        clock = pygame.time.Clock()
        self.create_random_huge_asteroids(num_asteroids=3)
        self.create_random_small_asteroids(num_asteroids=2)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()

            self.elapsed_time = 0.1
            self.handle_input()
            self.update_objects()
            self.check_collisions()
            font = pygame.font.Font(None, 48)
            score = font.render("Score: " + str(self.player.score), True, BLUE)
            self.screen.fill(BLACK)
            self.screen.blit(score, (30, 30))
            self.draw_objects()

            if self.game_over:
                if time.time() - self.game_over_time > 3:
                    pygame.quit()
                    sys.exit()
                self.screen.fill(BLACK)
                font = pygame.font.Font(None, 72)
                game_over_text = font.render("Game Over", True, WHITE)
                self.screen.blit(game_over_text, (self.screen_width // 2 - 132, self.screen_height // 2 - 40))

            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    game = AsteroidsGame(screen_width=1280, screen_height=720)
    game.run_game()
