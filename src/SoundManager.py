import pygame


class CircularButton:
    def __init__(self, x, y, radius, path, action_callback):
        self.x = x
        self.y = y
        self.radius = radius
        original_image = pygame.image.load(path)
        self.image = pygame.transform.scale(original_image, (2 * radius, 2 * radius))
        self.action_callback = action_callback

    def draw(self, screen):
        button_rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, button_rect.topleft)

    def is_clicked(self, mouse_pos):
        distance = pygame.math.Vector2(self.x - mouse_pos[0], self.y - mouse_pos[1]).length()
        return distance <= self.radius

    def handle_click(self):
        if self.action_callback:
            self.action_callback()


class SoundEffect:
    def __init__(self, sound_file, volume):
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound(sound_file)
        self.sound.set_volume(volume)

    def play(self):
        self.sound.play()

    def stop(self):
        self.sound.stop()

    def mute(self):
        self.sound.set_volume(0)

    def unmute(self):
        self.sound.set_volume(10)
