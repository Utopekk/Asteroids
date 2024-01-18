import pygame


class Particle:
    def __init__(self, x, y, color, lifetime, dx, dy):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.size = 3  # Size of the particle
        self.dx = dx
        self.dy = dy

    def update(self, elapsed_time):
        self.lifetime -= elapsed_time
        self.x += self.dx * elapsed_time
        self.y += self.dy * elapsed_time

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.size, self.size))