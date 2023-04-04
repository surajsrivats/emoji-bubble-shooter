import pygame
import random
import asyncio

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

    x = max(15, min(x, self.screen_width - 15))

    self.position = (x, y)

  def draw(self):
    emoji_position = (
        self.position[0] - self.current_emoji[1].get_width() // 2,
        self.position[1] - self.current_emoji[1].get_height() // 2
    )
    self.screen.blit(self.current_emoji[1], emoji_position)

  async def shoot_emoji(self, game):
    emoji_x, emoji_y = self.position

    async def gpt_callback(emoji_name):
      await game.story_queue.put(emoji_name)
      self.current_emoji = self.choose_next_emoji()

    await game.add_emoji_to_grid(self.current_emoji, (emoji_x, emoji_y), callback=lambda emoji_name: asyncio.create_task(gpt_callback(emoji_name)))