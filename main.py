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
    def __init__(self, n_size, x, y, dx, dy, angle, lives=3):
        super().__init__(n_size, x, y, dx, dy, angle)
        self.acceleration = 0.1
        self.speed = 10
        self.score = 0
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


class Enemy(SpaceObject):
    def __init__(self, screen, x, y, dx, dy, angle, shooting_interval=3.0):
        super().__init__(n_size=20.0, x=x, y=y, dx=dx, dy=dy, angle=angle)
        self.screen = screen
        self.shooting_interval = shooting_interval
        self.last_time_shot = 0

    def draw_enemy(self):
        pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(self.x, self.y, 30, 30))

    def shoot_bullet(self):
        bullet_speed = 10.0  # Adjust the speed of the bullet as needed
        bullet_direction = math.atan2(self.dy, self.dx)  # Use the direction of the enemy's movement
        bullet = EnemyBullet(
            n_size=0,
            x=self.x,
            y=self.y,
            dx=bullet_speed * math.cos(bullet_direction),
            dy=bullet_speed * math.sin(bullet_direction),
            angle=bullet_direction,
            acceleration=1
        )
        return bullet

    def update(self, player_x, player_y):
        # Adjust the enemy's position based on the player's position
        angle_to_player = math.atan2(player_y - self.y, player_x - self.x)
        self.dx = math.cos(angle_to_player) * 10  # Adjust the speed as needed
        self.dy = math.sin(angle_to_player) * 10  # Adjust the speed as needed

        now = time.time()
        if now - self.last_time_shot >= self.shooting_interval:
            bullet = self.shoot_bullet()
            self.last_time_shot = now
            return bullet


class EnemyBullet(SpaceObject):
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
        self.enemy = None
        self.player = Player(n_size=20.0, x=screen_width / 2.0, y=screen_height / 2.0, dx=0.0, dy=0.0, angle=0.0,
                             lives=3)

    def draw_life_icons(self):
        heart_icon = pygame.image.load("heartt.png")  # Adjust the path to your heart icon
        icon_width, icon_height = 40, 40  # Adjust the size of the heart icon
        spacing = 10

        for i in range(self.player.lives):
            x = self.screen_width - (i + 1) * (icon_width + spacing)
            y = spacing
            resized_heart = pygame.transform.scale(heart_icon, (icon_width, icon_height))
            self.screen.blit(resized_heart, (x, y))

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

        if hasattr(self, 'enemy'):
            self.enemy.x += self.enemy.dx * self.elapsed_time
            self.enemy.y += self.enemy.dy * self.elapsed_time
            self.enemy.x, self.enemy.y = self.wrap(self.enemy.x, self.enemy.y)

            # Enemy shooting logic
            enemy_bullet = self.enemy.update(self.player.x, self.player.y)
            if enemy_bullet:
                self.vec_bullets.append(enemy_bullet)

    def draw_objects(self):
        self.draw_asteroids()
        for bullet in self.vec_bullets:
            bullet.x += bullet.dx * self.elapsed_time * bullet.acceleration
            bullet.y += bullet.dy * self.elapsed_time * bullet.acceleration
            bullet.x, bullet.y = self.wrap(bullet.x, bullet.y)
            pygame.draw.rect(self.screen, WHITE, pygame.Rect(bullet.x, bullet.y, 5, 5))

        self.draw_player_ship()
        if hasattr(self, 'enemy'):
            self.enemy.draw_enemy()

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

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            flame_vertices = self.calculate_flame_vertices()
            pygame.draw.polygon(self.screen, (255, 165, 0), flame_vertices)

    def calculate_flame_vertices(self):
        flame_length = 40
        flame_width = 20
        flame_vertices = [
            (0, flame_length),
            (-flame_width / 2, 20),
            (flame_width / 2, 20)
        ]

        rotated_flame_vertices = rotate_vertices(flame_vertices, self.player.angle)

        translated_flame_vertices = [
            (x + self.player.x, y + self.player.y) for x, y in rotated_flame_vertices
        ]

        return translated_flame_vertices

    def create_enemy(self):
        x = random.uniform(0, self.screen_width)
        y = random.uniform(0, self.screen_height)

        # Ensure the enemy is not too close to the player
        while (
                self.player.x + 150 < x < self.player.x - 150 or
                self.player.y + 150 < y < self.player.y - 150
        ):
            x = random.uniform(0, self.screen_width)
            y = random.uniform(0, self.screen_height)

        self.enemy = Enemy(screen=self.screen, x=x, y=y, dx=0, dy=0, angle=0)

    def check_collisions(self):
        if self.game_over:
            return

        # Check collision between player and enemy bullets
        player_rect = pygame.Rect(self.player.x - 10, self.player.y - 24, 20, 34)  # Adjust hitbox as needed
        for enemy_bullet in self.vec_bullets[:]:
            enemy_bullet_rect = pygame.Rect(enemy_bullet.x, enemy_bullet.y, 5, 5)
            if player_rect.colliderect(enemy_bullet_rect):
                print("Game Over (Hit by enemy bullet)")
                self.game_over = True
                self.game_over_time = time.time()

        player_rect = pygame.Rect(self.player.x - 10, self.player.y - 24, 20, 34)  # Adjust hitbox as needed

        huge_asteroids_to_remove = []  # List to store huge asteroids that will be removed
        small_asteroids_to_add = []  # List to store new small asteroids

        for asteroid in self.vec_huge_asteroids:
            rotated_vertices = rotate_vertices(asteroid.vertices, asteroid.angle)
            min_x = min(x for x, y in rotated_vertices)
            min_y = min(y for x, y in rotated_vertices)
            max_x = max(x for x, y in rotated_vertices)
            max_y = max(y for x, y in rotated_vertices)
            asteroid_rect = pygame.Rect(min_x + asteroid.x, min_y + asteroid.y, max_x - min_x, max_y - min_y)

            if player_rect.colliderect(asteroid_rect):
                print("Hit by huge asteroid")
                huge_asteroids_to_remove.append(asteroid)
                self.player.lives -= 1
                if self.player.lives <= 0:
                    print("Game Over")
                    self.game_over = True
                    self.game_over_time = time.time()

        for asteroid in self.vec_small_asteroids[:]:
            rotated_vertices = rotate_vertices(asteroid.vertices, asteroid.angle)
            min_x = min(x for x, y in rotated_vertices)
            min_y = min(y for x, y in rotated_vertices)
            max_x = max(x for x, y in rotated_vertices)
            max_y = max(y for x, y in rotated_vertices)
            asteroid_rect = pygame.Rect(min_x + asteroid.x, min_y + asteroid.y, max_x - min_x, max_y - min_y)

            # Check collision between player and asteroid hitbox
            if player_rect.colliderect(asteroid_rect) and asteroid not in huge_asteroids_to_remove:
                print("Hit by small asteroid")
                self.vec_small_asteroids.remove(asteroid)
                self.player.lives -= 1
                if self.player.lives <= 0:
                    print("Game Over")
                    self.game_over = True
                    self.game_over_time = time.time()

            # Check collision between bullets and asteroid hitbox
            for bullet in self.vec_bullets[:]:
                bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)
                if asteroid_rect.colliderect(bullet_rect):
                    self.vec_bullets.remove(bullet)
                    huge_asteroids_to_remove.append(asteroid)

                    # Divide the huge asteroid into two even smaller asteroids
                    x = asteroid.x
                    y = asteroid.y
                    small_asteroids_to_add.append(Asteroid(
                        n_size=random.randint(5, 12),
                        x=x + random.uniform(-10, 10),
                        y=y + random.uniform(-10, 10),
                        dx=random.uniform(-10, 10),
                        dy=random.uniform(-10, 10),
                        angle=random.uniform(0, 2 * math.pi),
                        vertices=generate_irregular_shape(random.randint(5, 12))
                    ))
                    small_asteroids_to_add.append(Asteroid(
                        n_size=random.randint(5, 12),
                        x=x + random.uniform(-10, 10),
                        y=y + random.uniform(-10, 10),
                        dx=random.uniform(-10, 10),
                        dy=random.uniform(-10, 10),
                        angle=random.uniform(0, 2 * math.pi),
                        vertices=generate_irregular_shape(random.randint(5, 12))
                    ))
                    self.player.score += 50

        for asteroid in huge_asteroids_to_remove:
            self.vec_huge_asteroids.remove(asteroid)

        self.vec_small_asteroids.extend(small_asteroids_to_add)

    def run_game(self):
        clock = pygame.time.Clock()
        self.create_random_huge_asteroids(num_asteroids=3)
        self.create_random_small_asteroids(num_asteroids=2)
        self.create_enemy()
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

            if hasattr(self, 'enemy'):
                enemy_bullet = self.enemy.update(self.player.x, self.player.y)
                if enemy_bullet:
                    self.vec_bullets.append(enemy_bullet)

            self.check_collisions()
            font = pygame.font.Font(None, 48)
            score = font.render("Score: " + str(self.player.score), True, BLUE)
            self.screen.fill(BLACK)
            self.draw_life_icons()
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
