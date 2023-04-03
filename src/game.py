import pygame
import random
import time
from player import Player

class Game:
  def __init__(self, screen, player, emoji_images):
    self.screen = screen
    self.grid = []
    self.score = 0
    self.start_time = time.time()
    self.player = player
    self.emoji_images = emoji_images
    self.generate_grid()

    self.emoji_width = self.emoji_images[0].get_width()
    self.emoji_height = self.emoji_images[0].get_height()

    self.last_layer_time = time.time()

  def generate_grid(self):
    ROWS = 14
    COLUMNS = 7
    # Make a two-dimensional array
    grid = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]

    # Fill the top row with random emojis
    for j in range(COLUMNS):
      grid[0][j] = random.choice(self.emoji_images)

    self.grid = grid

  def draw_grid(self):
    for y, row in enumerate(self.grid):
      for x, emoji in enumerate(row):
        if emoji is not None:  # Add this line to check if the emoji is not None
          position = (x * self.emoji_width, y * self.emoji_height + 105)
          scaled_emoji = pygame.transform.scale(emoji, (int(self.emoji_width), int(self.emoji_height)))
          self.screen.blit(scaled_emoji, position)

  def add_top_layer(self):
    ROWS = 14
    COLUMNS = 7
    new_row = [random.choice(self.emoji_images) for _ in range(COLUMNS)]
    self.grid = [new_row] + self.grid[:-1]

  def compress_grid(self):
    for j in range(len(self.grid[0])):
      top = 0
      for i in range(len(self.grid)):
        if self.grid[i][j] is not None:
          self.grid[top][j] = self.grid[i][j]
          top += 1
      
      # Fill the remaining cells with None
      while top < len(self.grid):
        self.grid[top][j] = None
        top += 1
              
  def check_game_over(self):
    for j in range(len(self.grid[-1])):
      if self.grid[-1][j] is not None:
        return True
    return False

  def find_matches(self, target, start_position):
    visited = set()
    matches = []

    def dfs(row, col, target):
      if row < 0 or row >= len(self.grid) or col < 0 or col >= len(self.grid[0]) or (row, col) in visited:
        return

      if self.grid[row][col] != target:
        return

      visited.add((row, col))
      matches.append((row, col))

      dfs(row-1, col, target)
      dfs(row+1, col, target)
      dfs(row, col-1, target)
      dfs(row, col+1, target)

    row, col = start_position
    dfs(row, col, target)
    return matches

  def add_emoji_to_grid(self, emoji, position):
    emoji_x, emoji_y = position
    grid_x, grid_y = int(emoji_x // self.emoji_width), int(emoji_y // self.emoji_height)

    if 0 <= grid_x < len(self.grid[0]):
      # Find the highest empty position in the column
      highest_empty_row = -1
      for row in range(len(self.grid)):
        if self.grid[row][grid_x] is None:
          highest_empty_row = row
          break

      if highest_empty_row != -1:
        self.grid[highest_empty_row][grid_x] = emoji

        # Check for matches
        matches = self.find_matches(emoji, (highest_empty_row, grid_x))

        if len(matches) >= 5:  # Minimum number of emojis to pop
          for row, col in matches:
            self.grid[row][col] = None  # Remove the emoji from the grid
          self.score += len(matches) * 10


  def update(self):
    self.compress_grid()

    if time.time() - self.last_layer_time >= 3:
      self.add_top_layer()
      self.last_layer_time = time.time()

    if self.check_game_over():
      print("Game over!")
      print("Score:", self.score)
      pygame.quit()
      quit()