from HandleManager import *
from SoundManager import SoundEffect


class CollisionManager:
    def __init__(self, player, vec_huge_asteroids, vec_medium_asteroids, vec_small_asteroids, vec_bullets,
                 handle_manager, collision_sound_path, vec_particles, game_over):
        self.player = player
        self.vec_huge_asteroids = vec_huge_asteroids
        self.vec_medium_asteroids = vec_medium_asteroids
        self.vec_small_asteroids = vec_small_asteroids
        self.vec_bullets = vec_bullets
        self.Utils = Utils()
        self.handle_manager = handle_manager
        self.ColisionSound = SoundEffect(collision_sound_path, 1.0)
        self.vec_particles = vec_particles
        self.game_over = game_over

    def handle_player_asteroid_collision(self, asteroid):
        self.handle_manager.handle_player_asteroid_collision(asteroid, self.vec_particles)

    def handle_bullet_asteroid_collision(self, asteroid):
        return self.handle_manager.handle_bullet_asteroid_collision(asteroid, self.vec_particles)

    def handle_game_over(self, reason):
        self.handle_manager.handle_game_over(reason)

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
                if self.player.lives <= 0:
                    self.handle_game_over("Game Over")

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
                        self.ColisionSound.play()
                        break

                if asteroid_hit:
                    break

        for bullet in bullets_to_remove:
            self.vec_bullets.remove(bullet)
    '''
    def check_player_bullet_enemy_collision(self):
        if self.game_over['status'] or not self.enemy:
            return

        enemy_rect = pygame.Rect(self.enemy.x+10, self.enemy.y+20, 80, 60)

        for bullet in self.vec_bullets:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)
            if bullet_rect.colliderect(enemy_rect) and bullet.can_damage_enemy:
                self.handle_player_bullet_enemy_collision(bullet)
    '''
    def check_collisions(self):
        if self.game_over:
            return

        player_rect = pygame.Rect(self.player.x - 10, self.player.y - 24, 20, 34)

        self.check_player_collision_with_asteroids(player_rect)
        self.check_player_with_enemy_bullet_collision(player_rect)

        self.check_bullet_asteroid_collisions()


