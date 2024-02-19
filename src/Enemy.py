from SpaceObject import SpaceObject
from EnemyBullet import EnemyBullet
import pygame
import math
import time
from Settings import BulletDeploySound, RED


class Enemy(SpaceObject):
    def __init__(self, screen, start_position, shooting_interval=3.0):
        if start_position == "top_left":
            super().__init__(n_size=20.0, x=0, y=0, dx=1, dy=0, angle=0)
        elif start_position == "top_right":
            super().__init__(n_size=20.0, x=screen.get_width(), y=0, dx=-1, dy=0, angle=0)
        elif start_position == "bottom_left":
            super().__init__(n_size=20.0, x=0, y=screen.get_height(), dx=1, dy=0, angle=0)
        elif start_position == "bottom_right":
            super().__init__(n_size=20.0, x=screen.get_width(), y=screen.get_height(), dx=-1, dy=0, angle=0)

        self.screen = screen
        self.shooting_interval = shooting_interval
        self.last_time_shot = 0
        self.enemy_image = pygame.image.load("resources\\enemy.svg")

        self.crossed_center = False

    def draw_enemy(self):
        self.screen.blit(self.enemy_image, (self.x, self.y))

 

    def shoot_bullet(self, player_x, player_y):
        bullet_speed = 60.0
        bullet_direction = math.atan2(player_y - self.y, player_x - self.x)
        bullet = EnemyBullet(
            n_size=0,
            x=self.x + 50,
            y=self.y + 50,
            dx=bullet_speed * math.cos(bullet_direction),
            dy=bullet_speed * math.sin(bullet_direction),
            angle=bullet_direction,
            acceleration=1
        )
        return bullet

    def update(self, player_x, player_y):
        if not self.crossed_center:
            if (
                    (self.dx > 0 and self.x >= self.screen.get_width() / 2) or
                    (self.dx < 0 and self.x <= self.screen.get_width() / 2)
            ):
                self.crossed_center = True
                self.dy = 1

        angle_to_player = math.atan2(player_y - self.y, player_x - self.x)
        speed_factor = 2
        self.dx = math.cos(angle_to_player) * speed_factor

        self.x += self.dx
        self.y += self.dy

        now = time.time()
        if now - self.last_time_shot >= self.shooting_interval:
            bullet = self.shoot_bullet(player_x, player_y)
            if bullet and time.time() > bullet.damage_activation_time:
                bullet.can_damage_enemy = True
            BulletDeploySound.play()
            self.last_time_shot = now
            return bullet
