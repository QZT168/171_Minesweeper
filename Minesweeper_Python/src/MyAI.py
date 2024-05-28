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

import itertools
from AI import AI
from Action import Action


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		self.rowDimension = rowDimension
		self.colDimension = colDimension
		self.totalMines = totalMines
		self.remainMines = totalMines
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
				# check uncover tiles with remaining adjacent tiles > 0
				if (self.board[row][col][0] != '_') and (self.board[row][col][0] > 0) and (self.board[row][col][2] > 0) and (self.X != col or self.Y != row):
					covers = self.update_effective_covered(col, row)
					if covers:
						self.check_effective_label(col, row, covers)

		# print board
		# for i in range(self.rowDimension - 1, -1, -1):
		# 	row = self.board[i]
		# 	print("\t".join([f"{col[0]}:{col[1]}:{col[2]}" for col in row]))


		if (not self.to_be_uncover) and (self.uncover_count != self.colDimension * self.rowDimension - self.totalMines):
			self.special_case()
			if (not self.to_be_uncover):
				remains = []
				for row in range(self.rowDimension):
					for col in range(self.colDimension):
						if (self.board[row][col][0] == '_'):
							remains.append((col, row))

				# print(f"remains: {remains}")
				if remains:
					self.guess_action(remains)
		
		# Return Action() according to different conditions
		# If all non-mine tiles are found, leave
		if self.uncover_count == self.colDimension * self.rowDimension - self.totalMines:
			return Action(AI.Action.LEAVE, self.X, self.Y)
		# If there's still a remaining non-mine tile, uncover
		elif self.to_be_uncover:

			# print(self.to_be_uncover)

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
				if (0 <= nearX < self.colDimension) and (0 <= nearY < self.rowDimension) and (nearX != self.X or nearY != self.Y):
					if self.board[nearY][nearX][0] == '_':  # cover now
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
				if (tile[0], tile[1]) not in self.to_be_uncover:
					self.to_be_uncover.append( (tile[0], tile[1]) )  # append (x,y)
			self.board[y][x][1] = 0  # update effectve label as 0
			self.board[y][x][2] = 0  # remaining = 0
		elif effective_label == len(covered):  # All the remaining tiles are mine
			for tile in covered:
				self.board[tile[1]][tile[0]][0] = -1  # labeled as mine
				self.update_adjacent_effective(tile[0], tile[1])
			self.board[y][x][1] = 0  # update effectve label as 0
			self.board[y][x][2] = 0  # remaining = 0

	def update_effective_covered(self, x, y):
		cover_tiles = []  # Store the adjacent tiles which are still covered.
		count_mines = 0
		for dx in [-1, 0, 1]:
			for dy in [-1, 0, 1]:
				nearX = x + dx
				nearY = y + dy
				if (0 <= nearX < self.colDimension) and (0 <= nearY < self.rowDimension) and (nearX != x or nearY != y):
					if self.board[nearY][nearX][0] == -1:
						count_mines += 1
					elif self.board[nearY][nearX][0] == '_':  # covered and unmarked tiles
						cover_tiles.append((nearX, nearY))
		self.board[y][x][1] = self.board[y][x][0] - count_mines  # update the current tile's effectiveLabel
		self.board[y][x][2] = len(cover_tiles)  # update the current tile's adjacent counter
		return cover_tiles

	def update_adjacent_effective(self, x, y):
		for dx in [-1, 0, 1]:
			for dy in [-1, 0, 1]:
				nearX = x + dx
				nearY = y + dy
				if (0 <= nearX < self.colDimension) and (0 <= nearY < self.rowDimension) and (nearX != x or nearY != y) \
					and (self.board[nearY][nearX][1] != " ") and (self.board[nearY][nearX][1] > 0):
					self.update_effective_covered(nearX, nearY)

	def guess_action(self, covered):
		mine_prob = {}
		for tile in covered:
			prob = 0
			x = tile[0]
			y = tile[1]
			for dx in [-1, 0, 1]: 
				for dy in [-1, 0, 1]:
					nearX = x + dx
					nearY = y + dy
					# check the adjacent tile of current covered tile is in bound, have effective label > 0
					if (0 <= nearX < self.colDimension) and (0 <= nearY < self.rowDimension) and (nearX != x or nearY != y) \
						and (self.board[nearY][nearX][1] != ' ') and (self.board[nearY][nearX][1] > 0):
						# effective label > 0, prob+=1
						prob += 1
			mine_prob[tile] = prob

		min_prob_tile = min(mine_prob, key=mine_prob.get)
		min_x = min_prob_tile[0]
		min_y = min_prob_tile[1]

		if (min_x, min_y) not in self.to_be_uncover:  # add to to_be_uncover list
			self.to_be_uncover.append((min_x, min_y))
	
	def special_case(self):
		orlist1 = []  # if (A or B) and (A or B or C), then C = 0(safe)
		orlist2 = []
		orlist3 = []
		orlist4 = []
		safes = []
		for row in range(self.rowDimension):
			for col in range(self.colDimension):
				# effective label = 1, remaining > 1
				if (self.board[row][col][1] != " ") and (self.board[row][col][1] == 1) and (self.board[row][col][2] > 1):
					covered = self.update_effective_covered(col, row)
					if covered not in orlist1:
						orlist1.append(covered)
				elif (self.board[row][col][1] != " ") and (self.board[row][col][1] == 2) and (self.board[row][col][2] > 2):
					covered = self.update_effective_covered(col, row)
					if covered not in orlist2:
						orlist2.append(covered)
				elif (self.board[row][col][1] != " ") and (self.board[row][col][1] == 3) and (self.board[row][col][2] > 3):
					covered = self.update_effective_covered(col, row)
					if covered not in orlist1:
						orlist3.append(covered)
				elif (self.board[row][col][1] != " ") and (self.board[row][col][1] == 4) and (self.board[row][col][2] > 4):
					covered = self.update_effective_covered(col, row)
					if covered not in orlist1:
						orlist4.append(covered)
		# sort orlist and check if the short one is included by the longer one
		if orlist1:
			orlist1.sort(key=len)
			self.include_relation(orlist1, safes)
		if orlist2:
			orlist2.sort(key=len)
			self.include_relation(orlist2, safes)
			self.exclude_mine(orlist1, orlist2)
		if orlist3:
			orlist3.sort(key=len)
			self.include_relation(orlist3, safes)
			self.exclude_mine(orlist2, orlist3)
			self.exclude_mine(orlist1, orlist3, diff=2)
		if orlist4:
			orlist4.sort(key=len)
			self.include_relation(orlist4, safes)
			self.exclude_mine(orlist3, orlist4)
			self.exclude_mine(orlist1, orlist4, diff=3)
		
		# add safe tiles to uncover list
		for safe in safes:
			if safe not in self.to_be_uncover:
				self.to_be_uncover.append(safe)

	def include_relation(self, orlist, safes):
		# check if the short one is included by the longer one
		for i in range(len(orlist)):
			for j in range(len(orlist)):
				if orlist[i] != orlist[j] and set(orlist[i]).issubset(set(orlist[j])):  # shorter one is included by the longer one
					for tile in orlist[j]:
						if tile not in orlist[i] and tile not in safes:
							safes.append(tile)  # the longer different ones are safe

	def exclude_mine(self, orlistA, orlistB, diff=1):
		for l1 in orlistA:
			for l2 in orlistB:
				if (len(l2) - len(l1) == diff) and (set(l1).issubset(set(l2))):
					for tile in l2:
						if tile not in l1:
							self.board[tile[1]][tile[0]][0] = -1
							# update the adjacent effective label
							self.update_adjacent_effective(tile[0], tile[1])
					

	
	# def model_check(self, covered):
	# 	print("model_check")
	# 	# generate all assignment combinations
	# 	all_assignments = list(itertools.product([0, -1], repeat=len(covered)))
	# 	valid_assignments = []
	# 	mine_probs = {}
	# 	# find valid assignments
	# 	for assign in all_assignments:
	# 		print("check assign:", assign)
	# 		for i in range(len(covered)):
	# 			x = covered[i][0]
	# 			y = covered[i][1]
	# 			self.board[y][x][0] = assign[i]
	# 		if self.is_valid(assign):
	# 			valid_assignments.append(assign)
	# 		# recover to original state (covered)
	# 		for i in range(len(covered)):
	# 			x = covered[i][0]
	# 			y = covered[i][1]
	# 			self.board[y][x][0] = '_'
	# 	# calculate prob of mine for each covered tiles
	# 	for j in range(len(covered)):
	# 		prob = 0
	# 		for valid in valid_assignments:
	# 			if valid[j] == -1:
	# 				prob += 1
	# 		mine_probs[covered[j]] = prob
	# 	# choose min_prob_tile
	# 	print(f"mine_probs: {mine_probs}")
	# 	min_prob_tile = min(mine_probs, key=mine_probs.get)
	# 	print(f"min_prob_tile: {min_prob_tile}")
	# 	min_x = min_prob_tile[0]
	# 	min_y = min_prob_tile[1]

	# 	# if (min_x, min_y) not in self.to_be_uncover:  # add to to_be_uncover list
	# 	# 	self.to_be_uncover.append((min_x, min_y))
	# 	return (min_x, min_y)

	
	# def is_valid(self, assignment):
	# 	for row in range(self.rowDimension):
	# 		for col in range(self.colDimension):
	# 			# check uncover tiles with number > 0, effective label > 0
	# 			if (self.board[row][col][0] != '_') and (self.board[row][col][0] > 0) and (self.board[row][col][1] > 0) and (self.X != col or self.Y != row):
	# 				checked_valid = self.update_effective_covered(col, row)
	# 				if checked_valid == [-1]:
	# 					return False
	# 	return True
