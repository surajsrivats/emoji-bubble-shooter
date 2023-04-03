import pygame
import math
import random

class Player:
  def __init__(self, screen, emoji_images):
    self.screen = screen
    self.screen_width, self.screen_height = self.screen.get_size()
    self.position = (self.screen_width // 2, self.screen_height - 15)
    self.emoji_images = emoji_images
    self.current_emoji = self.choose_next_emoji()
    self.speed = 30

  def choose_next_emoji(self):
    return random.choice(self.emoji_images)

  def update_position(self, key):
    x, y = self.position
    if key == pygame.K_a:
      x -= self.speed
    elif key == pygame.K_d:
      x += self.speed

    # Keep the player within the screen bounds
    x = max(15, min(x, self.screen_width - 15))

    self.position = (x, y)

  def draw(self):
    shooter_rect = pygame.Rect(self.position[0] - 25, self.position[1] - 25, 50, 50)

    emoji_position = (
        self.position[0] - self.current_emoji.get_width() // 2,
        self.position[1] - self.current_emoji.get_height() // 2
    )
    self.screen.blit(self.current_emoji, emoji_position)

  def shoot_emoji(self, game):
    emoji_x, emoji_y = self.position

    game.add_emoji_to_grid(self.current_emoji, (emoji_x, emoji_y))
    self.current_emoji = self.choose_next_emoji()