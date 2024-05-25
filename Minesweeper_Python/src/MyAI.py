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
		self.X = startX  # X = 0 means col 1
		self.Y = startY  # Y = 0 means row 1
		# Create a board to store the state, [state, effectiveLabel, remainAdjacent]
		# state: '_' = covered, -1 = mine, n = label; effectiveLabel: ' ' = unknown
		self.board = result = [[['_',' ',8] for c in range(self.colDimension)] for r in range(self.rowDimension)]
		# Store tiles that is not a mine and to be uncover
		self.to_be_uncover = []
		# Count the uncovers, so we can leave if we have uncovered all the non-mine tiles
		self.uncover_count = 1

	def getAction(self, number: int) -> "Action Object":

		# print("NUMBER:", number)
		# print("SelfX:", self.X, "SelfY:", self.Y)

		# Initilize the current tile state
		self.board[self.Y][self.X][0] = number
		covered = self.update_effective_covered(self.X, self.Y)  # update the effectiveLabel and coveredCounter
		# If current tile state is 0, all adjacent tiles are 0 as well.
		if number == 0:
			self.label_as_safe()
		# If number > 0, check adjacent tiles' states
		elif number > 0:
			self.check_effective_label(self.X, self.Y, covered)
		# Check effective label for other tiles after update the board state
		for row in range(self.rowDimension):
			for col in range(self.colDimension):
				if (self.board[row][col][0] != '_') and (self.board[row][col][0] > 0) and (self.board[row][col][2] > 0) and (self.X != col or self.Y != row):
					covers = self.update_effective_covered(col, row)
					self.check_effective_label(col, row, covers)

		# print board
		# for i in range(self.rowDimension - 1, -1, -1):
		# 	row = self.board[i]
		# 	print("\t".join([f"{col[0]}:{col[1]}:{col[2]}" for col in row]))
		
		# Return Action() according to different conditions
		# If all non-mine tiles are found, leave
		if self.uncover_count == self.colDimension * self.rowDimension - self.totalMines:
			return Action(AI.Action.LEAVE, self.X, self.Y)
		# If there's still a remaining non-mine tile, uncover
		elif self.to_be_uncover:
			# print(self.to_be_uncover)
			self.X, self.Y = self.to_be_uncover.pop(0)
			self.uncover_count += 1
			# print(self.uncover_count)
			# print(self.X, self.Y)
			# print("REAL:", self.X+1, self.Y+1)
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
					if self.board[nearY][nearX][0] == '_':
						self.board[nearY][nearX][0] = 0  # label as safe
						if (nearX, nearY) not in self.to_be_uncover:  # add to to_be_uncover list
							self.to_be_uncover.append((nearX, nearY))
		self.board[self.Y][self.X][1] = 0  # Effective Label = 0
		self.board[self.Y][self.X][2] = 0  # Remaining covered adjacent tiles = 0

	def check_effective_label(self, x, y, covered):
		effective_label = self.board[y][x][1]
		if effective_label == 0:  # All the remaining tiles are safe, label the remaining adjacent as safe
			for tile in covered:
				self.board[tile[1]][tile[0]][0] = 0  # tile[0] = x, tile[1] = y, board[y][x]
				if (tile[0],tile[1]) not in self.to_be_uncover:
					self.to_be_uncover.append( (tile[0],tile[1]) )  # append (x,y)
			self.board[y][x][1] = 0  # update effectve label as 0
			self.board[y][x][2] = 0  # remaining = 0
		elif effective_label == len(covered):  # All the remaining tiles are mine
			for tile in covered:
				self.board[tile[1]][tile[0]][0] = -1  # labeled as mine
			self.board[y][x][1] = 0  # update effectve label as 0
			self.board[y][x][2] = 0  # remaining = 0
		# else:  # need more mines
	
	def update_effective_covered(self, x, y):
		cover_tiles = []  # Store the adjacent tiles which are still covered.
		count_mines = 0
		for dx in [-1, 0, 1]:
			for dy in [-1, 0, 1]:
				nearX = x + dx
				nearY = y + dy
				if 0 <= nearX < self.colDimension and 0 <= nearY < self.rowDimension and (nearX != x or nearY != y):
					if self.board[nearY][nearX][0] == -1:
						count_mines += 1
					elif self.board[nearY][nearX][0] == '_':
						cover_tiles.append((nearX, nearY))
		self.board[y][x][1] = self.board[y][x][0] - count_mines  # update the current tile's effectiveLabel
		self.board[y][x][2] = len(cover_tiles)  # update the current tile's adjacent counter
		return cover_tiles

