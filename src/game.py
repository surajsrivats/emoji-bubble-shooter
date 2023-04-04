import pygame
import random
import time
from player import Player
import openai
import asyncio
import aiohttp


class Game:
	def __init__(self, screen, player, emoji_images):
		self.screen = screen
		self.score = 0
		self.start_time = time.time()
		self.player = player
		self.emoji_images = emoji_images
		self.emoji_width = self.emoji_images[0][1].get_width()
		self.emoji_height = self.emoji_images[0][1].get_height()
		self.last_layer_time = time.time()
		self.story = []
		self.story_queue = asyncio.Queue()

		self.grid = self.generate_grid()

	def generate_grid(self):
		rows, columns = 14, 7
		grid = [[None] * columns for _ in range(rows)]
		grid[0] = [random.choice(self.emoji_images) for _ in range(columns)]
		return grid

	def draw_grid(self):
		for y, row in enumerate(self.grid):
			for x, emoji in enumerate(row):
				if emoji:
					position = x * self.emoji_width, y * self.emoji_height + 105
					scaled_emoji = pygame.transform.scale(emoji[1], (self.emoji_width, self.emoji_height))
					self.screen.blit(scaled_emoji, position)

	def add_top_layer(self):
		new_row = [random.choice(self.emoji_images) for _ in range(len(self.grid[0]))]
		self.grid = [new_row] + self.grid[:-1]

	def compress_grid(self):
		for j in range(len(self.grid[0])):
			top = 0
			for i in range(len(self.grid)):
				if self.grid[i][j]:
					self.grid[top][j] = self.grid[i][j]
					top += 1
			while top < len(self.grid):
				self.grid[top][j] = None
				top += 1

	def check_game_over(self):
		return any(self.grid[-1])

	def find_matches(self, target, start_position):
		visited, matches = set(), []

		def dfs(row, col):
			if not (0 <= row < len(self.grid) and 0 <= col < len(self.grid[0]) and (row, col) not in visited and self.grid[row][col] == target):
				return

			visited.add((row, col))
			matches.append((row, col))

			for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
				dfs(row + dr, col + dc)

		dfs(*start_position)
		return matches

	async def generate_story_line(self, emoji_name):
		async with aiohttp.ClientSession() as session:
			data = {
				"model": "gpt-3.5-turbo",
				"messages": [
					{"role": "system", "content": "You are a masterful storyteller who weaves tales of the fantastic stories from the simplest details. Let's begin with a brand new story!"},
					{"role": "assistant", "content": ". ".join(self.story)},
					{"role": "user", "content": f"What happens next to the {emoji_name} oh wise storyteller? Build upon the previous story you were telling, but please limit it to one sentence"}
				]
			}

			async with session.post("https://api.openai.com/v1/chat/completions", json=data, headers={"Authorization": f"Bearer {openai.api_key}"}) as response:
				completion = await response.json()
				story_line = completion["choices"][0]["message"]["content"]

				print(emoji_name, ": ", story_line, "\n")
				return story_line

	async def add_emoji_to_grid(self, emoji, position, callback=None):
		emoji_x, emoji_y = position
		grid_x, grid_y = emoji_x // self.emoji_width, emoji_y // self.emoji_height

		if 0 <= grid_x < len(self.grid[0]):
			highest_empty_row = next((row for row in range(len(self.grid)) if self.grid[row][grid_x] is None), -1)

			if highest_empty_row != -1:
				self.grid[highest_empty_row][grid_x] = emoji
				matches = self.find_matches(emoji, (highest_empty_row, grid_x))

				if len(matches) >= 5:
					for row, col in matches:
						self.grid[row][col] = None
					self.score += len(matches) * 10

					if callback:
						await callback(emoji[0])

	def update(self):
		self.compress_grid()

		if time.time() - self.last_layer_time >= 4:
			self.add_top_layer()
			self.last_layer_time = time.time()

		if self.check_game_over():
			print("Game over!")
			print("Score:", self.score)
			pygame.quit()
			quit()