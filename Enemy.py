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

    enemy_image = pygame.image.load("enemy.svg")
