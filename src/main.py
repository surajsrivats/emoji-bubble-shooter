import os
import pygame
import time
import openai
from game import Game
from player import Player

# Initialize Pygame and set up the game window
pygame.init()
screen = pygame.display.set_mode((210, 525))
pygame.display.set_caption("Emoji Bubble Shooter")


def load_emoji_images():
  emoji_image_names = ['tiger.png', 'monkey.png', 'sun.png']
  emoji_images = []

  for name in emoji_image_names:
    image_path = os.path.join('../assets', 'sprites', name)
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (30, 30))
    emoji_images.append(image)

  return emoji_images

# Load emoji images
emoji_images = load_emoji_images()

# Initialize the game
player = Player(screen, emoji_images)
game = Game(screen, player, emoji_images)

# Functions
# def generate_story(emoji_group):
#   # Add logic to interact with GPT and generate a story line based on the emoji group
#   pass

# Game loop
running = True
clock = pygame.time.Clock()
FPS = 60

def draw_text(screen, text, size, x, y, color=(0, 0, 0)):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)

while running:
    clock.tick(FPS)
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:  # Handle user input for moving the player and shooting the emoji
            if event.key == pygame.K_a or event.key == pygame.K_d:
                player.update_position(event.key)
            elif event.key == pygame.K_SPACE:
                player.shoot_emoji(game)
                pygame.display.flip()
                player.current_emoji = player.choose_next_emoji()

    # Update game state
    game.update()

    # Draw the game screen
    game.draw_grid()
    player.draw()

    # Display the score
    score_text = f"Score: {game.score}"
    draw_text(screen, score_text, 36, screen.get_width() // 2, 10)

    # Display the timer
    timer = int(time.time() - game.start_time)
    timer_text = f"Time: {timer}s"
    draw_text(screen, timer_text, 36, screen.get_width() // 2, 50)

    pygame.display.flip()

pygame.quit()