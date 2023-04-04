import os
import pygame
import time
import openai
import asyncio
from dotenv import load_dotenv
from game import Game
from player import Player

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = openai_api_key

pygame.init()
screen = pygame.display.set_mode((210, 525))
pygame.display.set_caption("Emoji Bubble Shooter")


def load_emoji_images():
  emoji_image_names = ['tiger.png', 'monkey.png', 'sun.png']
  emoji_images = []

  for name in emoji_image_names:
    image_path = os.path.join('../assets', 'sprites', name)
    image = pygame.image.load(image_path).convert_alpha()
    image = pygame.transform.scale(image, (30, 30))

    emoji_images.append((name.split('.')[0], image))

  return emoji_images


emoji_images = load_emoji_images()

player = Player(screen, emoji_images)
game = Game(screen, player, emoji_images)


def draw_text(screen, text, size, x, y, color=(0, 0, 0)):
  font = pygame.font.Font(None, size)
  text_surface = font.render(text, True, color)
  text_rect = text_surface.get_rect()
  text_rect.midtop = (x, y)
  screen.blit(text_surface, text_rect)


async def process_story_queue(game):
  while True:
    emoji_name = await game.story_queue.get()
    story_line = await game.generate_story_line(emoji_name)
    game.story.append(story_line)
    game.story_queue.task_done()


async def main():
  running = True
  clock = pygame.time.Clock()
  FPS = 60

  asyncio.create_task(process_story_queue(game))

  while running:
    clock.tick(FPS)
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      elif event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_a, pygame.K_d):
          player.update_position(event.key)
        elif event.key == pygame.K_SPACE:
          await player.shoot_emoji(game)
          pygame.display.flip()
    await asyncio.sleep(1 / FPS)

    game.update()
    game.draw_grid()
    player.draw()

    draw_text(screen, f"Score: {game.score}", 36, screen.get_width() // 2, 10)
    draw_text(screen, f"Time: {int(time.time() - game.start_time)}s", 36, screen.get_width() // 2, 50)

    pygame.display.flip()

  await game.story_queue.join()
  pygame.quit()

asyncio.run(main())