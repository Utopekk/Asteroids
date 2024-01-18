import sys

sys.path.append('src')
import random
import os
from pygame import FULLSCREEN
from src.Bullet import *
from src.Asteroid import *
from src.Player import *
from src.Enemy import *
from src.Particle import *
from src.Settings import *
from src.Stage import *
import time

N = 4


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


def get_rotated_rect(vertices, angle, x, y):
    rotated_vertices = rotate_vertices(vertices, angle)
    min_x = min(x for x, y in rotated_vertices)
    min_y = min(y for x, y in rotated_vertices)
    max_x = max(x for x, y in rotated_vertices)
    max_y = max(y for x, y in rotated_vertices)
    return pygame.Rect(min_x + x, min_y + y, max_x - min_x, max_y - min_y)


def med_asteroids(asteroid):
    medium_asteroids = Asteroid(
        n_size=random.randint(20, 30),
        x=asteroid.x + random.uniform(-10, 10),
        y=asteroid.y + random.uniform(-10, 10),
        dx=random.uniform(-25, 25),
        dy=random.uniform(-25, 25),
        angle=random.uniform(0, 2 * math.pi),
        vertices=generate_irregular_shape(random.randint(28, 35))
    )
    return medium_asteroids


def sma_asteroids(asteroid):
    small_asteroids = Asteroid(
        n_size=random.randint(12, 20),
        x=asteroid.x + random.uniform(-10, 10),
        y=asteroid.y + random.uniform(-10, 10),
        dx=random.uniform(-25, 25),
        dy=random.uniform(-25, 25),
        angle=random.uniform(0, 2 * math.pi),
        vertices=generate_irregular_shape(random.randint(15, 20))
    )
    return small_asteroids


def on_button_click():
    print("Button Clicked!")


class AsteroidsGame:
    def __init__(self):
        self.elapsed_time = None
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Asteroids")
        self.vec_huge_asteroids = []
        self.vec_medium_asteroids = []
        self.vec_small_asteroids = []
        self.vec_bullets = []
        self.interval_shooting = 0.4
        self.last_time_shot = 0
        self.counter_shooting = 0
        self.game_over = False
        self.game_over_time = 0
        self.enemy = None
        self.stage = Stage(1)
        self.score = 0
        self.score1 = 0
        self.enemy = None
        self.player = Player(n_size=20.0, x=WIDTH / 2, y=HEIGHT / 2, dx=0.0, dy=0.0, angle=0.0,
                             lives=3)
        self.vec_particles = []
        self.player_respawn_timer = 0
        self.BulletDeploySound = pygame.mixer.Sound("resources\\363698__jofae__retro-gun-shot.mp3")
        self.BulletDeploySound.set_volume(0.1)
        self.ColisionSound = pygame.mixer.Sound("resources\\170144__timgormly__8-bit-explosion2.mp3")
        self.ColisionSound.set_volume(0.1)
        self.GameOverSound = pygame.mixer.Sound("resources\\412168__screamstudio__arcade-game-over.wav")
        self.GameOverSound.set_volume(0.1)

    def adjust_resolution(self):
        monitor_info = pygame.display.Info()
        monitor_width = monitor_info.current_w
        monitor_height = monitor_info.current_h
        self.screen = pygame.display.set_mode((monitor_width, monitor_height), pygame.FULLSCREEN)

    def create_particle_effect(self, x, y, color, num_particles):
        for _ in range(num_particles):
            lifetime = random.uniform(0.2, 0.5)
            dx = random.uniform(-50, 50)
            dy = random.uniform(-50, 50)
            particle = Particle(x, y, color, lifetime, dx, dy)
            self.vec_particles.append(particle)

    # ... (existing methods)

    def update_particles(self, elapsed_time):
        self.vec_particles = [particle for particle in self.vec_particles if particle.lifetime > 0]
        for particle in self.vec_particles:
            particle.update(elapsed_time)

    def draw_particles(self):
        for particle in self.vec_particles:
            particle.draw(self.screen)

    def draw_life_icons(self):
        icon_width, icon_height = 40, 60
        spacing = 10
        player_color = RED

        for i in range(self.player.lives):
            x = WIDTH - (i + 1) * (icon_width + spacing)
            y = spacing

            vertices = [(x, y + icon_height), (x + icon_width, y + icon_height), (x + icon_width / 2, y)]
            pygame.draw.polygon(self.screen, player_color, vertices, 2)

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

            self.player.speed = math.sqrt(self.player.dx ** 2 + self.player.dy ** 2)

            max_speed = 140.0
            if self.player.speed > max_speed:
                scale_factor = max_speed / self.player.speed
                self.player.dx *= scale_factor
                self.player.dy *= scale_factor

        elif not (self.player.speed <= 10):
            damping_factor = 0.98
            self.player.dx *= damping_factor
            self.player.dy *= damping_factor
            self.player.speed = math.sqrt(self.player.dx ** 2 + self.player.dy ** 2)
        if keys[pygame.K_F11]:
            if self.screen.get_flags() & FULLSCREEN:
                info_object = pygame.display.Info()
                monitor_width = info_object.current_w
                monitor_height = info_object.current_h
                pygame.display.set_mode((monitor_width, monitor_height))
            else:
                pygame.display.set_mode((WIDTH, HEIGHT), FULLSCREEN)
        firing_position = self.player.calculate_firing_position()
        now = float(time.time())
        if keys[pygame.K_SPACE] and (
                now - self.last_time_shot) >= self.interval_shooting and self.player.destroyed is False:
            self.BulletDeploySound.play()
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
        if hasattr(self, 'enemy'):
            self.enemy.x += self.enemy.dx * self.elapsed_time
            self.enemy.y += self.enemy.dy * self.elapsed_time
            self.enemy.x, self.enemy.y = wrap(self.enemy.x, self.enemy.y)

            enemy_bullet = self.enemy.update(self.player.x, self.player.y)
            if enemy_bullet:
                self.vec_bullets.append(enemy_bullet)

    def update_objects(self):
        self.vec_bullets = [b for b in self.vec_bullets if time.time() - b.creation_time <= 1]

        for bullet in self.vec_bullets:
            bullet.x += bullet.dx * self.elapsed_time * bullet.acceleration
            bullet.y += bullet.dy * self.elapsed_time * bullet.acceleration
            bullet.x, bullet.y = wrap(bullet.x, bullet.y)

        for asteroid in self.vec_huge_asteroids:
            asteroid.x += asteroid.dx * self.elapsed_time
            asteroid.y += asteroid.dy * self.elapsed_time
            asteroid.x, asteroid.y = wrap(asteroid.x, asteroid.y)

        for asteroid in self.vec_medium_asteroids:
            asteroid.x += asteroid.dx * self.elapsed_time
            asteroid.y += asteroid.dy * self.elapsed_time
            asteroid.x, asteroid.y = wrap(asteroid.x, asteroid.y)

        for asteroid in self.vec_small_asteroids:
            asteroid.x += asteroid.dx * self.elapsed_time
            asteroid.y += asteroid.dy * self.elapsed_time
            asteroid.x, asteroid.y = wrap(asteroid.x, asteroid.y)

        self.player.x += self.player.dx * self.elapsed_time
        self.player.y += self.player.dy * self.elapsed_time
        self.player.x, self.player.y = wrap(self.player.x, self.player.y)

        if self.player.destroyed and time.time() >= self.player_respawn_timer:
            self.player.x = WIDTH / 2.0
            self.player.y = HEIGHT / 2.0
            self.player.angle = 0.0
            self.player.dx = 0.0
            self.player.dy = 0.0
            self.player.destroyed = False

        if hasattr(self, 'enemy'):
            self.enemy.x += self.enemy.dx * self.elapsed_time
            self.enemy.y += self.enemy.dy * self.elapsed_time
            self.enemy.x, self.enemy.y = wrap(self.enemy.x, self.enemy.y)

            enemy_bullet = self.enemy.update(self.player.x, self.player.y)
            if enemy_bullet:
                self.vec_bullets.append(enemy_bullet)

    def draw_huge_asteroid_outline(self, asteroid):
        rotated_vertices = rotate_vertices(asteroid.vertices, asteroid.angle)
        translated_vertices = [(x + asteroid.x, y + asteroid.y) for x, y in rotated_vertices]

        # Draw outline for huge asteroid
        pygame.draw.polygon(self.screen, WHITE, translated_vertices, 2)

    def draw_objects(self):
        self.draw_asteroids()

        for bullet in self.vec_bullets:
            bullet.x += bullet.dx * self.elapsed_time * bullet.acceleration
            bullet.y += bullet.dy * self.elapsed_time * bullet.acceleration
            bullet.x, bullet.y = wrap(bullet.x, bullet.y)
            pygame.draw.rect(self.screen, WHITE, pygame.Rect(bullet.x, bullet.y, 5, 5))

        for asteroid in self.vec_medium_asteroids:
            self.draw_asteroid_outline(asteroid)

        for asteroid in self.vec_small_asteroids:
            self.draw_asteroid_outline(asteroid)

        if hasattr(self, 'enemy'):
            self.enemy.draw_enemy()

        self.draw_player_ship()
        self.draw_life_icons()

        pygame.display.flip()

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
        self.create_random_asteroids(num_asteroids,
                                     (50 + self.stage.asteroidDifficultySize, 80 + self.stage.asteroidDifficultySize),
                                     is_huge=True)

    def draw_asteroids(self):
        for asteroid in self.vec_huge_asteroids:
            self.draw_huge_asteroid_outline(asteroid)
        for asteroid in self.vec_small_asteroids:
            self.draw_huge_asteroid_outline(asteroid)

    def draw_asteroid_outline(self, asteroid):
        rotated_vertices = rotate_vertices(asteroid.vertices, asteroid.angle)
        translated_vertices = [(x + asteroid.x, y + asteroid.y) for x, y in rotated_vertices]

        # Draw filled asteroid
        pygame.draw.polygon(self.screen, BLACK, translated_vertices)

        # Draw outline
        pygame.draw.polygon(self.screen, WHITE, translated_vertices, 2)

    def draw_player_ship(self):
        if self.player.destroyed:
            return
        vertices = self.player.calculate_firing_position()

        # Draw outline for player's ship
        pygame.draw.polygon(self.screen, RED, vertices, 2)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            flame_vertices = self.calculate_flame_vertices()

            # Draw outline for flame
            pygame.draw.polygon(self.screen, (255, 165, 0), flame_vertices, 2)

        # Draw filled polygon
        pygame.draw.polygon(self.screen, BLACK, vertices)

        # Draw outline
        pygame.draw.polygon(self.screen, RED, vertices, 2)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            flame_vertices = self.calculate_flame_vertices()
            pygame.draw.polygon(self.screen, BLACK, flame_vertices)  # Draw filled flame
            pygame.draw.polygon(self.screen, (255, 165, 0), flame_vertices, 2)  # Draw flame outline

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

    def check_player_collision_with_asteroids(self, player_rect):
        for asteroid in self.vec_small_asteroids[:]:
            asteroid_rect = get_rotated_rect(asteroid.vertices, asteroid.angle, asteroid.x, asteroid.y)
            if player_rect.colliderect(asteroid_rect):
                self.handle_player_asteroid_collision(asteroid)

        for asteroid in self.vec_medium_asteroids[:]:
            asteroid_rect = get_rotated_rect(asteroid.vertices, asteroid.angle, asteroid.x, asteroid.y)
            if player_rect.colliderect(asteroid_rect):
                self.handle_player_asteroid_collision(asteroid)

        for asteroid in self.vec_huge_asteroids[:]:
            asteroid_rect = get_rotated_rect(asteroid.vertices, asteroid.angle, asteroid.x, asteroid.y)
            if player_rect.colliderect(asteroid_rect):
                self.handle_player_asteroid_collision(asteroid)

    def check_player_with_enemy_bullet_collision(self, player_rect):
        for enemy_bullet in self.vec_bullets[:]:
            enemy_bullet_rect = pygame.Rect(enemy_bullet.x, enemy_bullet.y, 5, 5)
            if player_rect.colliderect(enemy_bullet_rect):
                self.vec_bullets.remove(enemy_bullet)
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.handle_game_over("Game Over")

    def handle_player_asteroid_collision(self, asteroid):
        if self.player.destroyed:
            return
        if asteroid in self.vec_huge_asteroids:
            self.vec_huge_asteroids.remove(asteroid)
        elif asteroid in self.vec_medium_asteroids:
            self.remove_asteroid(asteroid)
        elif asteroid in self.vec_small_asteroids:
            self.vec_small_asteroids.remove(asteroid)

        self.player.lives -= 1

        if self.player.lives > 0:
            self.create_particle_effect(self.player.x, self.player.y, WHITE, 3)
            self.player.destroyed = True
            self.player_respawn_timer = time.time() + 2
            self.ColisionSound.play()
        else:
            self.handle_game_over("Game Over")

        if not (self.vec_huge_asteroids or self.vec_medium_asteroids or self.vec_small_asteroids):
            self.create_random_huge_asteroids(num_asteroids=N)

    def check_bullet_asteroid_collisions(self):
        bullets_to_remove = []

        for bullet in self.vec_bullets:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)
            asteroid_hit = False

            for asteroid_group in [self.vec_huge_asteroids, self.vec_medium_asteroids, self.vec_small_asteroids]:
                for asteroid in asteroid_group:
                    asteroid_rect = get_rotated_rect(asteroid.vertices, asteroid.angle, asteroid.x, asteroid.y)

                    if bullet_rect.colliderect(asteroid_rect):
                        if self.handle_bullet_asteroid_collision(asteroid):
                            bullets_to_remove.append(bullet)
                        asteroid_hit = True
                        self.ColisionSound.play()
                        break

                if asteroid_hit:
                    break

        for bullet in bullets_to_remove:
            self.vec_bullets.remove(bullet)

    last_asteroid_generation_time = 0

    def handle_bullet_asteroid_collision(self, asteroid):
        if asteroid in self.vec_huge_asteroids:
            self.score += 20
            self.score1 += 20
            self.vec_huge_asteroids.remove(asteroid)
            medium_asteroid_1 = med_asteroids(asteroid)
            medium_asteroid_2 = med_asteroids(asteroid)

            self.vec_medium_asteroids.extend([medium_asteroid_1, medium_asteroid_2])

        elif asteroid in self.vec_medium_asteroids:
            self.score += 50
            self.score1 += 50
            self.remove_asteroid(asteroid)

        elif asteroid in self.vec_small_asteroids:
            self.score += 100
            self.score1 += 100
            self.vec_small_asteroids.remove(asteroid)

        self.create_particle_effect(asteroid.x, asteroid.y, WHITE, 3)
        return True

    def handle_game_over(self, reason):
        print(reason)
        self.game_over = True
        self.GameOverSound.play()
        self.game_over_time = time.time()

    def check_collisions(self):
        if self.game_over:
            return

        player_rect = pygame.Rect(self.player.x - 10, self.player.y - 24, 20, 34)

        self.check_player_collision_with_asteroids(player_rect)
        self.check_player_with_enemy_bullet_collision(player_rect)

        self.check_bullet_asteroid_collisions()

        if self.score1 == 10000 and self.player.lives < 3:
            self.player.lives += 1
            self.score1 = 0

    def remove_asteroid(self, asteroid):
        self.vec_medium_asteroids.remove(asteroid)
        small_asteroid_1 = sma_asteroids(asteroid)
        small_asteroid_2 = sma_asteroids(asteroid)
        self.vec_small_asteroids.extend([small_asteroid_1, small_asteroid_2])

    st = 1
    count = 0
    delay = 0

    def run_game(self):
        clock = pygame.time.Clock()
        self.create_random_huge_asteroids(num_asteroids=N)
        self.create_enemy()
        game_running = True

        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
            if not self.game_over:
                self.elapsed_time = 0.1
                self.handle_input()
                self.update_objects()
                self.update_particles(self.elapsed_time)
                self.check_collisions()

            if not self.game_over:
                font = pygame.font.Font(None, 48)
                score_text = "Score: " + str(self.score)
                score = font.render(score_text, True, BLUE)
                self.screen.fill(BLACK)
                self.draw_life_icons()
                self.screen.blit(score, (30, 30))
                font = pygame.font.Font(None, 48)
                stage_text = "Stage: " + str(self.stage.stage)
                stage = font.render(stage_text, True, BLUE)
                self.screen.blit(stage, (30, 70))
                self.draw_objects()
                self.draw_particles()

                if self.score >= 99990:
                    font = pygame.font.Font(None, 72)
                    won_text = font.render("YOU WON!", True, WHITE)
                    self.screen.blit(won_text, (WIDTH // 2 - 132, HEIGHT // 2 - 40))
                    pygame.display.flip()
                    pygame.time.delay(3000)
                    game_running = False

                num_current_asteroids = len(self.vec_huge_asteroids) + len(self.vec_medium_asteroids) + len(
                    self.vec_small_asteroids) + self.delay
                if (
                        num_current_asteroids == 0 or 2.00 - self.stage.intervalSpawning <= time.time() - self.last_asteroid_generation_time <= 10.0):
                    if self.count < self.stage.newAsteroids:
                        if self.delay == 1:
                            self.st += 1
                            self.stage = Stage(self.st)
                        if self.delay == 2:
                            self.count += 1
                            self.create_random_huge_asteroids(num_asteroids=1)
                        else:
                            self.delay += 1
                        self.last_asteroid_generation_time = time.time()
                if time.time() - self.last_asteroid_generation_time >= 10.0:
                    self.count = 0
                    self.delay = 0

            if self.game_over:
                if time.time() - self.game_over_time > 3:
                    game_running = False
                else:
                    self.screen.fill(BLACK)
                    font = pygame.font.Font(None, 72)
                    game_over_text = font.render("Game Over", True, WHITE)
                    self.screen.blit(game_over_text, (WIDTH // 2 - 132, HEIGHT // 2 - 40))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = AsteroidsGame()
    game.run_game()
