"""
	Copyright (C) 2021  Torenir

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from random import randint
import pyglet
from pyglet.window import key as KEY

GAMESPEED = 10
RESOLUTION = (600, 600) #must be divisible by 10
SNAKECOLOR = ((230, 120, 20), (220, 155, 30)) #(HEAD, BODY)
FRUITCOLOR = (220, 33, 43)
BACKGROUND = (94, 166, 30, 255)
BLOCKIMAGE = pyglet.resource.image('block.png')
snakeIsDead = 0 #if 1 stops game. changing to 0 will resume (not implemented)


class Block(pyglet.sprite.Sprite):
	"""The primary part of game. It's just a color block 10x10 px and it moves"""
	def __init__(self, x, y, axis, direction, image, color):
		super(Block, self).__init__(image)
		self.x = x
		self.y = y
		self.axis = axis
		self.direction = direction
		self.color = color

	def move(self, axis, direction):
		self.direction = direction
		self.axis = axis
		if axis:
			self.y += direction * 10
		else:
			self.x += direction * 10


class Fruit(Block):
	"""When called creates a fruit on a random place on the map"""
	def __init__(self):
		super(Fruit, self).__init__( \
			randint(0, (RESOLUTION[1]-10)//10)*10, randint(0, \
			(RESOLUTION[0]-10)//10)*10, 1, 1, BLOCKIMAGE, FRUITCOLOR)


class Snake(object):
	"""Body of the player. It is a list of moving Blocks"""
	def __init__(self, heading):
		super(Snake, self).__init__()
		#creates snakes head in the middle of screen
		self.snakeBody = [Block(RESOLUTION[0]//2, RESOLUTION[1]//2, \
		heading[0], heading[1], BLOCKIMAGE, SNAKECOLOR[0])]

		self.grow(); self.grow() #add two additional blocks to snakes body

	def grow(self):
		lastBlock = self.snakeBody[-1] #gets last block in snakes body
		axis = lastBlock.axis
		direction = lastBlock.direction
		#creates coordinates for the new last block based on previous one
		if not axis:
			x = lastBlock.x - direction * 10
			y = lastBlock.y
		else:
			x = lastBlock.x
			y = lastBlock.y - direction * 10
		#adds new last block to snakes body
		self.snakeBody.append(Block(x, y, axis, direction, BLOCKIMAGE, SNAKECOLOR[1]))

	def draw(self):
		#iterates through every block in snakes body from tail to head
		for block in self.snakeBody[::-1]:
			block.draw()

	def move(self, heading):
		global snakeIsDead

		#iterates through every body block that is not head
		#from the furthest to the closest to snakes head
		for i in range(len(self.snakeBody[1:]), 0, -1):
			#moves the block to the position of next block
			self.snakeBody[i].move(self.snakeBody[i-1].axis, \
			self.snakeBody[i-1].direction)

		self.snakeBody[0].move(heading[0], heading[1]) #moves snakes head

		#checks if snakes head touches any other block
		#It could be done in a previous loop but then the head was out
		#of sync with the rest of snakes body
		for i in range(len(self.snakeBody[1:]), 0, -1):
			if self.snakeBody[i].x == self.snakeBody[0].x and \
			self.snakeBody[i].y == self.snakeBody[0].y:
				snakeIsDead = 1

		#checks if snakes head is outside the map border
		x = self.snakeBody[0].x; y = self.snakeBody[0].y
		if x < 0 or x == RESOLUTION[1] or y < 0 or y == RESOLUTION[1]:
			snakeIsDead = 1


class Window(pyglet.window.Window):
	def __init__(self):
		super(Window, self).__init__(RESOLUTION[0], RESOLUTION[1])
		pyglet.clock.schedule_interval(self.update, GAMESPEED/100)
		self.snakeHeading = (0, 1) #default direction of the snake
		self.snake = Snake(self.snakeHeading) #creates player
		self.fruits = [Fruit(), Fruit()] #creates first two fruits on map

		#creates background for the game using given color
		self.background = pyglet.image.SolidColorImagePattern(BACKGROUND)
		self.background = self.background.create_image(RESOLUTION[0], RESOLUTION[1])

	def on_draw(self):
		self.clear()
		self.background.blit(0, 0) #draws background
		self.snake.draw()
		for fruit in self.fruits: fruit.draw() #draws all the fruits

	def on_key_press(self, symbol, modifiers):
		if symbol == KEY.W and self.snake.snakeBody[0].axis != 1:
			self.snakeHeading = (1, 1) #move up
		elif symbol == KEY.S and self.snake.snakeBody[0].axis != 1:
			self.snakeHeading = (1, -1) #move down
		elif symbol == KEY.A and self.snake.snakeBody[0].axis != 0:
			self.snakeHeading = (0, -1) #move left
		elif symbol == KEY.D and self.snake.snakeBody[0].axis != 0:
			self.snakeHeading = (0, 1) #move right
		elif symbol == KEY.ESCAPE:
			pyglet.app.exit()

	def update(self, dt):
		if not snakeIsDead: #check if snake is dead
				self.snake.move(self.snakeHeading) #move the snake in certain direction
				#iterates through fruits and checks if head touches them
				for fruit in self.fruits:
					if self.snake.snakeBody[0].x == fruit.x and \
					self.snake.snakeBody[0].y == fruit.y:
						fruit.delete()
						self.fruits.remove(fruit)
						self.snake.grow() #grow the snake after eating a fruit
						self.fruits.append(Fruit()) #create new fruit


window = Window()
pyglet.app.run()
