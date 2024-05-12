# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		self.rowDimension = rowDimension
		self.colDimension = colDimension
		self.totalMines = totalMines
		self.X = startX  # X = 0 means row 1
		self.Y = startY  # Y = 0 means col 1
		# Create a board to store the state
		self.board = result = [[None for _ in range(self.colDimension)] for _ in range(self.rowDimension)]
		# Store tiles that is not a mine and to be uncover
		self.to_be_uncover = []
		# Count the uncovers, so we can leave if we have uncovered all the non-mine tiles
		self.uncover_count = 1

	def getAction(self, number: int) -> "Action Object":
		# Initilize the current tile state
		self.board[self.Y][self.X] = number
		# If current tile state is 0, all adjacent tiles are 0 as well.
		if number == 0:
			self.label_as_safe()
		# if number > 0, check adjacent tiles' states
		elif number > 0:
			self.check_effective_label(self.X, self.Y, number)
			for row in range(self.rowDimension):
				for col in self.board[row]:
					if col is not None and col > 0:
						self.check_effective_label(col, row, col)
		
		# return Action()
		# If all non-mine tiles are found, leave
		if self.uncover_count == self.colDimension * self.rowDimension - self.totalMines:
			return Action(AI.Action.LEAVE, self.X, self.Y)
		# If there's still a remaining non-mine tile, uncover
		elif self.to_be_uncover:
			self.X, self.Y = self.to_be_uncover.pop(0)
			self.uncover_count += 1
			return Action(AI.Action.UNCOVER, self.X, self.Y)
		else:
			return Action(AI.Action.LEAVE, self.X, self.Y)
		

	def label_as_safe(self):
		for dx in [-1, 0, 1]:
			for dy in [-1, 0, 1]:
				nearX = self.X + dx
				nearY = self.Y + dy
				# Check if the adjacent xy is inside the boundary and is not itself.
				if 0 <= nearX < self.colDimension and 0 <= nearY < self.rowDimension and (nearX != self.X or nearY != self.Y):
					if self.board[nearY][nearX] is None:
						self.board[nearY][nearX] = 0  # label as safe
						if (nearX, nearY) not in self.to_be_uncover:  # add to to_be_uncover list
							self.to_be_uncover.append((nearX, nearY))

	def check_effective_label(self, x, y, number):
		cover_tiles = []  # Store the adjacent tiles which are still covered.
		count_flag = 0  # Count the number of adjacent tiles that has marked as mine
		for dx in [-1, 0, 1]:
			for dy in [-1, 0, 1]:
				nearX = x + dx
				nearY = y + dy
				if 0 <= nearX < self.colDimension and 0 <= nearY < self.rowDimension and (nearX != x or nearY != y):
					if self.board[nearY][nearX] == -1:
						count_flag += 1
					elif self.board[nearY][nearX] is None:
						cover_tiles.append((nearX, nearY))
		if (number - count_flag) == 0:  # No more mine near the tile
			for tile in cover_tiles:
				self.board[tile[1]][tile[0]] = 0  # tile[0] = x, tile[1] = y, board[y][x]
				if (tile[0],tile[1]) not in self.to_be_uncover:
					self.to_be_uncover.append( (tile[0],tile[1]) )  # append (x,y)
		if len(cover_tiles) == number - count_flag:  # All the remaining tiles are mine
			for tile in cover_tiles:
				self.board[tile[1]][tile[0]] = -1
