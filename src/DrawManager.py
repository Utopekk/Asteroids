from main import *
import math
from utils import Utils
import pygame


class DrawManager:
    def __init__(self, screen):
        self.screen = screen
        self.utils = Utils()

    def draw_huge_asteroid_outline(self, asteroid):
        rotated_vertices = self.utils.rotate_vertices(asteroid.vertices,
                                                      asteroid.angle)
        translated_vertices = [(x + asteroid.x, y + asteroid.y) for x, y in rotated_vertices]

        pygame.draw.polygon(self.screen, WHITE, translated_vertices, 2)

    def draw_asteroid_outline(self, asteroid):
        rotated_vertices = self.utils.rotate_vertices(asteroid.vertices, asteroid.angle)
        translated_vertices = [(x + asteroid.x, y + asteroid.y) for x, y in rotated_vertices]

        pygame.draw.polygon(self.screen, BLACK, translated_vertices)

        pygame.draw.polygon(self.screen, WHITE, translated_vertices, 2)

    def draw_asteroids(self, vec_huge_asteroids, vec_small_asteroids):
        for asteroid in vec_huge_asteroids:
            self.draw_huge_asteroid_outline(asteroid)
        for asteroid in vec_small_asteroids:
            self.draw_huge_asteroid_outline(asteroid)

    def draw_player_ship(self, player):
        if player.destroyed:
            return
        vertices = player.calculate_firing_position()

        pygame.draw.polygon(self.screen, RED, vertices, 2)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            flame_vertices = player.calculate_flame_vertices()

            pygame.draw.polygon(self.screen, (255, 165, 0), flame_vertices, 2)

        pygame.draw.polygon(self.screen, BLACK, vertices)

        pygame.draw.polygon(self.screen, RED, vertices, 2)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            flame_vertices = player.calculate_flame_vertices()
            pygame.draw.polygon(self.screen, BLACK, flame_vertices)
            pygame.draw.polygon(self.screen, (255, 165, 0), flame_vertices, 2)

    def draw_life_icons(self, player):
        icon_width, icon_height = 40, 60
        spacing = 10
        player_color = RED

        for i in range(player.lives):
            x = WIDTH - (i + 1) * (icon_width + spacing)
            y = spacing

            vertices = [(x, y + icon_height), (x + icon_width, y + icon_height), (x + icon_width / 2, y)]
            pygame.draw.polygon(self.screen, player_color, vertices, 2)

    def draw_particles(self, vec_particles):
        for particle in vec_particles:
            particle.draw(self.screen)

    def draw_objects(self, vec_huge_asteroids, vec_medium_asteroids, vec_small_asteroids, vec_bullets, player,
                     elapsed_time, vec_particles, enemy):
        self.draw_asteroids(vec_huge_asteroids, vec_small_asteroids)

        for bullet in vec_bullets:
            bullet.x += bullet.dx * elapsed_time * bullet.acceleration
            bullet.y += bullet.dy * elapsed_time * bullet.acceleration
            bullet.x, bullet.y = self.utils.wrap(bullet.x, bullet.y)
            pygame.draw.rect(self.screen, WHITE, pygame.Rect(bullet.x, bullet.y, 5, 5))

        for asteroid in vec_medium_asteroids:
            self.draw_asteroid_outline(asteroid)

        for asteroid in vec_small_asteroids:
            self.draw_asteroid_outline(asteroid)

        if enemy is not None:
            enemy.draw_enemy()

        self.draw_player_ship(player)
        self.draw_life_icons(player)
        self.draw_particles(vec_particles)

        pygame.display.flip()
