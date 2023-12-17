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