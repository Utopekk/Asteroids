import sys
import random
import os

sys.path.append('src')
from pygame import FULLSCREEN
from src.Settings import *
from src.Asteroid import *
from src.Player import *
from src.Enemy import *
from src.Particle import *
from src.Stage import *
from src.Bullet import *
from src.DrawManager import *
from src.Utils import *
from src.SoundManager import *

N = 4


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
        self.stage = Stage(1)
        self.score = 0
        self.score1 = 0
        self.enemy = None
        self.enemy_spawn_timer = None
        self.player = Player(n_size=20.0, x=WIDTH / 2, y=HEIGHT / 2, dx=0.0, dy=0.0, angle=0.0,
                             lives=3)
        self.vec_particles = []
        self.player_respawn_timer = 0
        self.draw_manager = DrawManager(self.screen)
        self.circular_mute_button = CircularButton(60, 1000, 60, cmb_image_path, self.on_button_click)
        self.circular_muted_button = CircularButton(60, 1000, 60, cdb_image_path, self.on_button_click)

        self.is_game_muted = False

    def on_button_click(self):
        if not self.is_game_muted:
            self.is_game_muted = True
            BulletDeploySound.mute()
            ColisionSound.mute()
            GameOverSound.mute()
        else:
            self.is_game_muted = False
            BulletDeploySound.unmute()
            ColisionSound.unmute()
            GameOverSound.unmute()

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

    def update_particles(self, elapsed_time):
        self.vec_particles = [particle for particle in self.vec_particles if particle.lifetime > 0]
        for particle in self.vec_particles:
            particle.update(elapsed_time)

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
            BulletDeploySound.play()
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

        if hasattr(self, 'enemy') and self.enemy is not None:
            self.enemy.x += self.enemy.dx * self.elapsed_time
            self.enemy.y += self.enemy.dy * self.elapsed_time
            self.enemy.x, self.enemy.y = Utils.wrap(self.enemy.x, self.enemy.y)

            enemy_bullet = self.enemy.update(self.player.x, self.player.y)
            if enemy_bullet:
                self.vec_bullets.append(enemy_bullet)

    def update_objects(self):
        self.vec_bullets = [b for b in self.vec_bullets if time.time() - b.creation_time <= 1]

        for bullet in self.vec_bullets:
            bullet.x += bullet.dx * self.elapsed_time * bullet.acceleration
            bullet.y += bullet.dy * self.elapsed_time * bullet.acceleration
            bullet.x, bullet.y = Utils.wrap(bullet.x, bullet.y)

        for asteroid in self.vec_huge_asteroids:
            asteroid.x += asteroid.dx * self.elapsed_time
            asteroid.y += asteroid.dy * self.elapsed_time
            asteroid.x, asteroid.y = Utils.wrap(asteroid.x, asteroid.y)

        for asteroid in self.vec_medium_asteroids:
            asteroid.x += asteroid.dx * self.elapsed_time
            asteroid.y += asteroid.dy * self.elapsed_time
            asteroid.x, asteroid.y = Utils.wrap(asteroid.x, asteroid.y)

        for asteroid in self.vec_small_asteroids:
            asteroid.x += asteroid.dx * self.elapsed_time
            asteroid.y += asteroid.dy * self.elapsed_time
            asteroid.x, asteroid.y = Utils.wrap(asteroid.x, asteroid.y)

        self.player.x += self.player.dx * self.elapsed_time
        self.player.y += self.player.dy * self.elapsed_time
        self.player.x, self.player.y = Utils.wrap(self.player.x, self.player.y)

        if self.player.destroyed and time.time() >= self.player_respawn_timer:
            self.player.x = WIDTH / 2.0
            self.player.y = HEIGHT / 2.0
            self.player.angle = 0.0
            self.player.dx = 0.0
            self.player.dy = 0.0
            self.player.destroyed = False

        if self.enemy is not None:  # Add this check
            enemy_rect = pygame.Rect(self.enemy.x, self.enemy.y, 40, 40)
            for asteroid_group in [self.vec_huge_asteroids, self.vec_medium_asteroids, self.vec_small_asteroids]:
                for asteroid in asteroid_group[:]:
                    asteroid_rect = Utils.get_rotated_rect(asteroid.vertices, asteroid.angle, asteroid.x, asteroid.y)
                    if enemy_rect.colliderect(asteroid_rect):
                        self.create_particle_effect(self.enemy.x, self.enemy.y, WHITE, 5)
                        del self.enemy
                        self.create_enemy()

                        if asteroid in self.vec_huge_asteroids:
                            self.vec_huge_asteroids.remove(asteroid)
                        elif asteroid in self.vec_medium_asteroids:
                            Utils.remove_asteroid(asteroid, self.vec_medium_asteroids, self.vec_small_asteroids)
                        elif asteroid in self.vec_small_asteroids:
                            self.vec_small_asteroids.remove(asteroid)

        self.vec_particles = [particle for particle in self.vec_particles if particle.lifetime > 0]
        for particle in self.vec_particles:
            particle.update(self.elapsed_time)

    def draw_huge_asteroid_outline(self, asteroid):
        rotated_vertices = Utils.rotate_vertices(asteroid.vertices, asteroid.angle)
        translated_vertices = [(x + asteroid.x, y + asteroid.y) for x, y in rotated_vertices]

        # Draw outline for huge asteroid
        pygame.draw.polygon(self.screen, WHITE, translated_vertices, 2)

    def create_enemy(self):
        start_positions = ["top_left", "top_right", "bottom_left", "bottom_right"]
        start_position = random.choice(start_positions)

        self.enemy = Enemy(screen=self.screen, start_position=start_position, shooting_interval=3.0)

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

    def check_player_collision_with_asteroids(self, player_rect):
        for asteroid in self.vec_small_asteroids[:]:
            asteroid_rect = Utils.get_rotated_rect(asteroid.vertices, asteroid.angle, asteroid.x, asteroid.y)
            if player_rect.colliderect(asteroid_rect):
                self.handle_player_asteroid_collision(asteroid)

        for asteroid in self.vec_medium_asteroids[:]:
            asteroid_rect = Utils.get_rotated_rect(asteroid.vertices, asteroid.angle, asteroid.x, asteroid.y)
            if player_rect.colliderect(asteroid_rect):
                self.handle_player_asteroid_collision(asteroid)

        for asteroid in self.vec_huge_asteroids[:]:
            asteroid_rect = Utils.get_rotated_rect(asteroid.vertices, asteroid.angle, asteroid.x, asteroid.y)
            if player_rect.colliderect(asteroid_rect):
                self.handle_player_asteroid_collision(asteroid)

    def check_player_with_enemy_bullet_collision(self, player_rect):
        for enemy_bullet in self.vec_bullets[:]:
            enemy_bullet_rect = pygame.Rect(enemy_bullet.x, enemy_bullet.y, 5, 5)
            if player_rect.colliderect(enemy_bullet_rect):
                self.vec_bullets.remove(enemy_bullet)
                self.player.lives -= 1
                self.player.destroyed = True
                if self.player.lives <= 0:
                    self.handle_game_over("Game Over")

    def handle_player_asteroid_collision(self, asteroid):
        if self.player.destroyed:
            return
        if asteroid in self.vec_huge_asteroids:
            self.vec_huge_asteroids.remove(asteroid)
        elif asteroid in self.vec_medium_asteroids:
            Utils.remove_asteroid(asteroid, self.vec_medium_asteroids, self.vec_small_asteroids)
        elif asteroid in self.vec_small_asteroids:
            self.vec_small_asteroids.remove(asteroid)

        self.player.lives -= 1

        if self.player.lives > 0:
            self.create_particle_effect(self.player.x, self.player.y, WHITE, 3)
            self.player.destroyed = True
            self.player_respawn_timer = time.time() + 2
            ColisionSound.play()
        else:
            self.handle_game_over("Game Over")

        if not (self.vec_huge_asteroids or self.vec_medium_asteroids or self.vec_small_asteroids):
            self.create_random_huge_asteroids(num_asteroids=N)

    last_asteroid_gen_time = 0

    def check_bullet_asteroid_collisions(self):
        bullets_to_remove = []

        for bullet in self.vec_bullets:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)
            asteroid_hit = False

            for asteroid_group in [self.vec_huge_asteroids, self.vec_medium_asteroids, self.vec_small_asteroids]:
                for asteroid in asteroid_group:
                    asteroid_rect = Utils.get_rotated_rect(asteroid.vertices, asteroid.angle, asteroid.x, asteroid.y)

                    if bullet_rect.colliderect(asteroid_rect):
                        if self.handle_bullet_asteroid_collision(asteroid):
                            bullets_to_remove.append(bullet)
                        asteroid_hit = True
                        ColisionSound.play()
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
            medium_asteroid_1 = Utils.med_asteroids(asteroid)
            medium_asteroid_2 = Utils.med_asteroids(asteroid)

            self.vec_medium_asteroids.extend([medium_asteroid_1, medium_asteroid_2])

        elif asteroid in self.vec_medium_asteroids:
            self.score += 50
            self.score1 += 50
            Utils.remove_asteroid(asteroid, self.vec_medium_asteroids, self.vec_small_asteroids)

        elif asteroid in self.vec_small_asteroids:
            self.score += 100
            self.score1 += 100
            self.vec_small_asteroids.remove(asteroid)

        self.create_particle_effect(asteroid.x, asteroid.y, WHITE, 3)
        return True

    def check_player_enemy_collision(self):
        if self.game_over or self.player.destroyed or not self.enemy:
            return

        player_rect = pygame.Rect(self.player.x - 10, self.player.y - 24, 20, 34)
     
        enemy_rect = pygame.Rect(self.enemy.x, self.enemy.y, 95, 95)
        if player_rect.colliderect(enemy_rect):
            self.handle_player_enemy_collision()

    def handle_player_enemy_collision(self):
        self.player.lives -= 1
        if self.player.lives > 0:
            self.create_particle_effect(self.player.x, self.player.y, WHITE, 3)
            self.player.destroyed = True
            self.player_respawn_timer = time.time() + 2
            ColisionSound.play()
        else:
            self.handle_game_over("Game Over")

    def check_player_bullet_enemy_collision(self):
        if self.game_over or not self.enemy:
            return

        enemy_rect = pygame.Rect(self.enemy.x+10, self.enemy.y+20, 80, 60)

        for bullet in self.vec_bullets:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)
            if bullet_rect.colliderect(enemy_rect) and bullet.can_damage_enemy:
                self.handle_player_bullet_enemy_collision(bullet)

    def handle_player_bullet_enemy_collision(self, bullet):
        self.vec_bullets.remove(bullet)
        self.create_particle_effect(self.enemy.x, self.enemy.y, WHITE, 3)
        ColisionSound.play()
        del self.enemy
        self.enemy = None
        self.enemy_spawn_timer = time.time() + 15

    def handle_game_over(self, reason):
        print(reason)
        self.game_over = True
        GameOverSound.play()
        self.game_over_time = time.time()

    def check_collisions(self):
        if self.game_over:
            return

        player_rect = pygame.Rect(self.player.x - 10, self.player.y - 24, 20, 34)

        self.check_player_collision_with_asteroids(player_rect)
        self.check_player_with_enemy_bullet_collision(player_rect)
        self.check_player_enemy_collision()
        self.check_bullet_asteroid_collisions()
        self.check_player_bullet_enemy_collision()

        if self.score1 == 10000 and self.player.lives < 3:
            self.player.lives += 1
            self.score1 = 0


    def run_game(self):
        clock = pygame.time.Clock()
        self.create_random_huge_asteroids(num_asteroids=3)
        game_running = True
        self.enemy_spawn_timer = time.time() + 3
        while game_running:
            self.screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        if self.circular_mute_button.is_clicked(mouse_pos):
                            self.circular_mute_button.handle_click()
            if not self.game_over:
                if time.time() >= self.enemy_spawn_timer and not self.enemy:
                    self.create_enemy()
                    self.enemy_spawn_timer = time.time() + 15
                self.elapsed_time = 0.1
                if not self.is_game_muted:
                    self.circular_mute_button.draw(self.screen)
                else:
                    self.circular_mute_button.draw(self.screen)
                    self.circular_muted_button.draw(self.screen)
                font = pygame.font.Font(None, 48)
                score_text = "Score: " + str(self.score)
                score = font.render(score_text, True, BLUE)
                self.screen.blit(score, (30, 30))
                font = pygame.font.Font(None, 48)
                stage_text = "Stage: " + str(self.stage.stage)
                stage = font.render(stage_text, True, BLUE)
                self.screen.blit(stage, (30, 70))
                self.handle_input()
                self.update_objects()
                self.update_particles(self.elapsed_time)
                self.check_collisions()
                self.draw_manager.draw_objects(self.vec_huge_asteroids, self.vec_medium_asteroids,
                                               self.vec_small_asteroids, self.vec_bullets, self.player,
                                               self.elapsed_time, self.vec_particles, self.enemy)
            if not self.game_over:
                if self.score >= 99990:
                    font = pygame.font.Font(None, 72)
                    won_text = font.render("YOU WON!", True, WHITE)
                    self.screen.blit(won_text, (WIDTH // 2 - 132, HEIGHT // 2 - 40))
                    pygame.display.flip()
                    pygame.time.delay(3000)
                    game_running = False

                num_curr_asteroids = len(self.vec_huge_asteroids) + len(self.vec_medium_asteroids) + len(
                    self.vec_small_asteroids)
                asteroid_timer = time.time()
                if num_curr_asteroids == 0 and asteroid_timer > 4:
                    self.stage.stage += 1
                    asteroid_timer = 0
                    self.create_random_huge_asteroids(num_asteroids=N)


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
