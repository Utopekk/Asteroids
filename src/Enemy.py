from SpaceObject import SpaceObject
from EnemyBullet import EnemyBullet
import pygame
import math
import time


class Enemy(SpaceObject):
    def __init__(self, screen, x, y, dx, dy, angle, shooting_interval=3.0):
        super().__init__(n_size=20.0, x=x, y=y, dx=dx, dy=dy, angle=angle)
        self.screen = screen
        self.shooting_interval = shooting_interval
        self.last_time_shot = 0
        self.enemy_image = pygame.image.load("resources\\enemy.svg")
    def draw_enemy(self):

        self.screen.blit(self.enemy_image, (self.x, self.y))

    def shoot_bullet(self, player_x, player_y):
        bullet_speed = 40.0
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
        angle_to_player = math.atan2(player_y - self.y, player_x - self.x)
        self.dx = math.cos(angle_to_player) * 10
        self.dy = 0

        now = time.time()
        if now - self.last_time_shot >= self.shooting_interval:
            bullet = self.shoot_bullet(player_x, player_y)
            self.last_time_shot = now
            return bullet

