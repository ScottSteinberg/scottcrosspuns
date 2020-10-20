
import time, random

# I like to keep track of function times as I generatd my puzzles
ijvertPairsListTime = 0
crosswordNotBlockedTime = 0
unijvertTime = 0
updateijvertTime = 0
insertTime = 0

# Also keep track of # of times each function is called
ijvertPairsListCalls = 0
crosswordNotBlockedCalls = 0
unijvertCalls = 0
updateijvertCalls = 0
insertCalls = 0
solveCalls = 0
the_time = time.time()

# The Crossword class makes an nxn crossword puzzle
class Crossword(object):
	def __init__(self, n, names, how_long = None, switch_time = 60, print_regenerate = False):
		self.n = n
		self.usedNames = []
		self.unusedNames = sorted(sorted(names), key = len, reverse = True)
		self.string = " "*n*n # Crossword implemented as a nxn string

		# As the puzzles generate, I print the ones with the highest score
		self.bestString = self.string
		self.bestScore = 0
		self.mostUsedNames = 0 

		# Store possible intersections for each letter
		self.ijvertPairs = dict()
		for p in range(97, 123):
			self.ijvertPairs[chr(p)] = set()

		self.strings = set()
		self.all_strings = set() # Only really relevant if clock is on
		self.empty = True

		# how_long is how long the algorithm runs before the puzzle regenerates
		# If nothing is inputted for how_long, the algorithm runs w/o regenerating
		if(how_long is None):
			self.clock = False
		else:
			self.clock = True
			self.how_long = how_long
			self.seconds = 0 # Total time algorithm runs
			self.result_seconds = 0 # Time since best score was found
			self.last_time = time.time() # Time of last regeneration
			self.result_last_time = time.time() # Time last best score was found
			self.switch_time = switch_time # Time algorithm runs before regenerating
			self.break_the_loop = False
			self.print_regenerate = print_regenerate

		# Find the best solution given nxn and names provided
		self.solutions = self.solve()

	def printPuzzles(self, rev = True, string = None):
		def printPuzzle(string, rev = False):
			puzzleString = ""
			for i in range(self.n):
				for j in range(self.n):
					if(rev): letter = string[j*self.n+i]
					else: letter = string[i*self.n+j]
					if(letter == " "): puzzleString += "- "
					else: puzzleString += letter + " "
				puzzleString += "\n"
			print(puzzleString)
		if(string is None): string = self.string
		printPuzzle(string)
		if(rev): printPuzzle(string, rev = True)


	def vertBlocked(self, i, j, name):
		# Check if letter in puzzle can be accessed vertically
		return(((i-1 >= 0 and self.string[((i-1)*self.n + j)] != " ") or 
                (i+len(name) < self.n and self.string[((i+len(name))*self.n + j)] != " ")))

	def horzBlocked(self, i, j, name):
		# Check if letter in puzzle can be accessed horizontally
		return((j-1 >= 0 and self.string[(i*self.n + j - 1)] != " ") or 
               (j+len(name) < self.n and self.string[(i*self.n + j + len(name))] != " "))


	def ijvertPairsList(self, name):
		# Function returns list of possible places the name can be inputted into the puzzle
		# ijvert pairs are just of row number, column number, and verticality
		### i = row in which the letter is found at
		### j = column in which the letter is found at
		### vert = Boolean: True if a word can be inserted vertically, False if horizontally

		# Keep track of time
		global ijvertPairsListTime, ijvertPairsListCalls
		ijvertPairsListCalls += 1
		x = time.time()

		pairs = set()
		nameLength = len(name)
		if(self.empty): # All possible places the longest word can be inputted
			for i in range(self.n):
				for j in range(self.n - nameLength + 1):
					pairs.add((i, j, False)) # The reverse puzzle would add (j, i, True) instead
		else:
			for k in range(nameLength):
				letter = name[k]
				ijvertPairs = self.ijvertPairs[letter]
				for i, j, vert in ijvertPairs:
					letter_at_ij = self.string[i*self.n + j]
					# Check if name could possibly be added vertically
					if(vert and nameLength <= self.n - (i-k) and 0 <= i-k and
        				not self.vertBlocked(i-k, j, name)):
						pairs.add(((i-k), j, vert))
					# Check if name could possibly be added horizontally
					elif(not vert and nameLength <= self.n - (j-k) and 0 <= j-k and
        				not self.horzBlocked(i, (j-k), name)):
						pairs.add((i, (j-k), vert))

		ijvertPairsListTime += time.time() - x 
		pairs = list(pairs)
		random.shuffle(pairs) # Shuffle so we don't get the same order each time
		return pairs

	def ijvertPairAddable(self, i, j, vert, k, new_string):
		# Determine if a word could be inserted at (i, j) given the new string crossword
		if(vert): # Determining if (i+k, j, True) is a feasible ijvertPair
			# If there isn't a vertical word in the puzzle, can't make a horizontal connection
			if((j==0 or new_string[((i+k)*self.n + j - 1)] == " ") and 
				new_string[((i+k)*self.n + j)] == " " and
				(j==self.n-1 or new_string[((i+k)*self.n + j + 1)] == " ")):
				return False
			return True
			'''
			# Puzzle loops through fewer ijvertPairs this way but may make code run slower
			return((j == 0 or not self.leftBlocked(i+k, j, new_string)) and
					(j == self.n-1 or not self.rightBlocked(i+k, j, new_string)) and
					(i+k == 0 or not self.upBlocked(i+k, j, new_string)) and
					(i+k == self.n-1 or not self.downBlocked(i+k, j, new_string)))
			'''

		else: # Determining if (i, j+k, False) is a feasible ijvertPair for letter
			# If there isn't a vertical word in the puzzle, can't make a horizontal connection
			if((i==0 or new_string[((i-1)*self.n + j + k)] == " ") and 
				new_string[(i*self.n + j + k)] == " " and
				(i==self.n-1 or new_string[((i+1)*self.n + j + k)] == " ")):
				return False
			return True
			'''
			# Puzzle loops through fewer ijvertPairs this way but may make code run slower
			return((j+k == 0 or not self.leftBlocked(i, j+k, new_string)) and
					(j+k == self.n-1 or not self.rightBlocked(i, j+k, new_string)) and
					(i == 0 or not self.upBlocked(i, j+k, new_string)) and
					(i == self.n-1 or not self.downBlocked(i, j+k, new_string))
			'''

	def leftBlocked(self, i, j, new_string):
		# Check if puzzle left of (i,j) is blocked
		if(j == 0): return True
		return( (new_string[(i*self.n + j - 1)] != " ") and 
				(i-1 < 0 or new_string[((i-1)*self.n + j - 1)] != " ") and 
				(i+1 >= self.n or new_string[((i+1)*self.n + j - 1)] != " "))

	def rightBlocked(self, i, j, new_string):
		# Check if puzzle right of (i,j) is blocked
		if(j == self.n - 1): return True
		return( (new_string[(i*self.n + j + 1)] != " ") and 
				(i-1 < 0 or new_string[((i-1)*self.n + j + 1)] != " ") and 
				(i+1 >= self.n or new_string[((i+1)*self.n + j + 1)] != " "))

	def upBlocked(self, i, j, new_string):
		# Check if puzzle above (i,j) is blocked
		if(i == 0): return True
		return( (new_string[((i-1)*self.n + j)] != " ") and 
				(j-1 < 0 or new_string[((i-1)*self.n + j - 1)] != " ") and 
				(j+1 >= self.n or new_string[((i-1)*self.n + j + 1)] != " "))

	def downBlocked(self, i, j, new_string):
		# Check if puzzle below (i,j) is blocked
		if(i == self.n - 1): return True
		return( (new_string[((i+1)*self.n + j)] != " ") and 
				(j-1 < 0 or new_string[((i+1)*self.n + j - 1)] != " ") and 
				(j+1 >= self.n or new_string[((i+1)*self.n + j + 1)] != " "))

	def updateijvert(self, i, j, letter, vert, k, replaced, new_string):
		# Keep track of time
		global updateijvertTime, updateijvertCalls
		updateijvertCalls += 1
		x = time.time()

		if(vert):
			# When updating, we check for discarding pairs in the row above
			# If we're at the last row, we can just discard pairs in the last row if necessary
			if(i+k == self.n-1): row = i+k
			else: row = i+k-1
			# If (i-1,j-1) is now blocked to the right because of the last letter we inserted
			if(i+k-1 >= 0 and j-1 >= 0 and self.rightBlocked(i+k-1, j-1, new_string)):
				left_letter = new_string[(row*self.n + j - 1)]
				if(k > 0 and left_letter != " "): 
					self.ijvertPairs[left_letter].discard((row, j-1, True))

			# If(i-1,j+1) is now blocked to the left because of the last letter we inserted
			if(i+k-1 >= 0 and j+1 < self.n and self.leftBlocked(i+k-1, j+1, new_string)):
				right_letter = new_string[(row*self.n + j + 1)]
				if(k > 0 and right_letter != " "):
					self.ijvertPairs[right_letter].discard((row, j+1, True))

			# We just added letter vertically here, so ijvert pair no longer valid
			self.ijvertPairs[letter].discard(((i+k), j, True))

			# If pair is addable, we can connect a letter horizontally here
			if(self.ijvertPairAddable(i, j, vert, k, new_string)):
				self.ijvertPairs[letter].add(((i+k), j, False))

		else:
			# When updating, we check for discarding pairs in the column to the left
			# If we're at the last column, we can just discard pairs in the last column if necessary
			if(j+k == self.n-1): col = j+k
			else: col = j+k-1			
			# If (i-1,j-1) is now blocked below because of the last letter we inserted
			if(i-1 >= 0 and j+k-1 >= 0 and self.downBlocked(i-1, j+k-1, new_string)):
				up_letter = new_string[((i-1)*self.n + col)]
				if(k > 0 and up_letter != " "): 
					self.ijvertPairs[up_letter].discard(((i-1), col, False))

			# If (i+1,j-1) is now blocked above because of the last letter we inserted
			if(i+1 < self.n and j+k-1 >= 0 and self.upBlocked(i+1, j+k-1, new_string)):
				down_letter = new_string[((i+1)*self.n + col)]
				if(k > 0 and down_letter != " "):
					self.ijvertPairs[down_letter].discard(((i+1), col, False))

			# We just added letter horizontally here, so ijvert pair no longer valid
			self.ijvertPairs[letter].discard((i, (j+k), False))

			# If pair is addable, we can connect a letter vertically here
			if(self.ijvertPairAddable(i, j, vert, k, new_string)):
				self.ijvertPairs[letter].add((i, (j+k), True))	

		updateijvertTime += time.time() - x
		return self

	def crosswordNotBlocked(self, i, j, name, vert, k):
		global crosswordNotBlockedTime, crosswordNotBlockedCalls
		crosswordNotBlockedCalls += 1
		x = time.time()
		if(self.empty): 
			crosswordNotBlockedTime += time.time() - x
			return True
		elif(vert):
			if(self.string[((i+k)*self.n + j)] == name[k]):
				crosswordNotBlockedTime += time.time() - x
				return True
			# If we find a letter at (i+k,j) or directly left or right
			elif(self.string[((i+k)*self.n + j)] != " "): 
				crosswordNotBlockedTime += time.time() - x
				return False
			elif(0 <= j-1 and self.string[((i+k)*self.n + j - 1)] != " "): 
				crosswordNotBlockedTime += time.time() - x
				return False
			elif(j+1 < self.n and self.string[((i+k)*self.n + j + 1)] != " "):
				crosswordNotBlockedTime += time.time() - x
				return False
		else: #not vert
			if(self.string[(i*self.n + j + k)] == name[k]):
				crosswordNotBlockedTime += time.time() - x
				return True
			# If we find a letter at (i,j+k) or directly above or below
			elif(self.string[(i*self.n + j + k)] != " "):
				crosswordNotBlockedTime += time.time() - x
				return False
			elif(0 <= i-1 and self.string[((i-1)*self.n + j + k)] != " "):
				crosswordNotBlockedTime += time.time() - x
				return False
			elif(i+1 < self.n and self.string[((i+1)*self.n + j + k)] != " "):
				crosswordNotBlockedTime += time.time() - x
				return False
		crosswordNotBlockedTime += time.time() - x
		return True

	def unijvert(self, i, j, letter, vert, k, name, new_string):
		# Same idea as updateijvert, but undoing everything if the insert doesn't work
		# or if we need to backtrack

		# Keep track of time
		global unijvertTime, unijvertCalls
		unijvertCalls += 1
		x = time.time()

		if(vert):
			self.ijvertPairs[letter].discard(((i+k), j, False))

			# If ijvert pairs were discarded in updateijvert, they'll be addable here
			if(self.ijvertPairAddable(i+k, j, vert, 0, self.string)):
				self.ijvertPairs[letter].add(((i+k), j, True))

			if(i+k == self.n-1): row = i+k
			else: row = i+k-1
			if(i+k-1 >= 0 and j+1 < self.n and self.leftBlocked(i+k-1, j+1, new_string)):
				right_letter = new_string[(row*self.n + j + 1)]
				if(k > 0 and right_letter != " " and 
					self.ijvertPairAddable(row, j+1, vert, 0, self.string)):
					self.ijvertPairs[right_letter].add((row, j+1, True))

			if(i+k-1 >= 0 and j-1 >= 0 and self.rightBlocked(i+k-1, j-1, new_string)):
				left_letter = new_string[(row*self.n + j - 1)]
				if(k > 0 and left_letter != " " and 
					self.ijvertPairAddable(row, j-1, vert, 0, self.string)): 				
					self.ijvertPairs[left_letter].add((row, j-1, True))

		else:		
			self.ijvertPairs[letter].discard((i, (j+k), True))	

			# If ijvert pairs were discarded in updateijvert, they'll be addable here
			if(self.ijvertPairAddable(i, j+k, vert, 0, self.string)):
				self.ijvertPairs[letter].add((i, (j+k), False))
			
			if(j+k == self.n-1): col = j+k
			else: col = j+k-1
			if(i+1 < self.n and j+k-1 >= 0 and self.upBlocked(i+1, j+k-1, new_string)):
				down_letter = new_string[((i+1)*self.n + col)]
				if(k > 0 and down_letter != " " and 
					self.ijvertPairAddable(i+1, col, vert, 0, self.string)):
					self.ijvertPairs[down_letter].add(((i+1), col, False))

			if(i-1 >= 0 and j+k-1 >= 0 and self.downBlocked(i-1, j+k-1, new_string)):
				if(j+k == self.n-1): col = j+k
				else: col = j+k-1
				up_letter = new_string[((i-1)*self.n + col)]
				if(k > 0 and up_letter != " " and 
					self.ijvertPairAddable(i-1, col, vert, 0, self.string)): 
					self.ijvertPairs[up_letter].add(((i-1), col, False))

		unijvertTime += time.time() - x
		return self


	def uninsert(self, i, j, vert, name, limit, new_string):
		for k in range(limit-1, -1, -1):
			letter = name[k]
			self.unijvert(i, j, letter, vert, k, name, new_string)

	def insert(self, i, j, name, vert):
		# Keep track of time
		global insertTime, insertCalls
		insertCalls += 1
		x = time.time()

		new_string = self.string # This is helpful to keep track of ijverts
		for k in range(len(name)):
			letter = name[k]
			if(self.crosswordNotBlocked(i, j, name, vert, k)):
				if(vert):
					replaced = self.string[((i+k)*self.n + j)]
					new_string = "".join([new_string[:((i+k)*self.n + j)], letter, new_string[((i+k)*self.n + j + 1):]])
				else:
					replaced = self.string[(i*self.n + j + k)]
					new_string = "".join([new_string[:(i*self.n + j + k)], letter, new_string[(i*self.n + j + k + 1):]])

				self.updateijvert(i, j, letter, vert, k, replaced, new_string)
			else: # nothing needs to be done if first letter is blocked
				if(k > 0): self.uninsert(i, j, vert, name, k, new_string)
				insertTime += time.time() - x
				return self

		# If we get to this point, we can change our string
		self.empty = False
		self.string = new_string
		self.unusedNames.remove(name)
		self.usedNames.append(name)

		# Update ijverts (still looking into this)
		'''
		if(vert and i-1 >= 0 and self.string[(i-1)*self.n + j] != " "):
			print("UPFIX", (i-1, j, True), (i-1, j, False), letter)
			self.ijvertPairs[self.string[(i-1)*self.n + j]].discard(((i-1), j, True))
			self.ijvertPairs[self.string[(i-1)*self.n + j]].discard(((i-1), j, False))
		if(vert and i+len(name) < self.n and self.string[(i+len(name))*self.n + j] != " "):
			print("DOWNFIX", (i+len(name), j, True), (i+len(name), j, False), letter)
			self.ijvertPairs[self.string[(i+len(name))*self.n + j]].discard(((i+len(name)), j, True))
			self.ijvertPairs[self.string[(i+len(name))*self.n + j]].discard(((i+len(name)), j, False))
		if(not vert and j-1 >= 0 and self.string[i*self.n + j - 1] != " "):
			print("LEFTFIX", (i, j-1, True), (i, j-1, False), letter)
			self.ijvertPairs[self.string[i*self.n + j - 1]].discard((i, (j-1), True))
			self.ijvertPairs[self.string[i*self.n + j - 1]].discard((i, (j-1), False))
		if(not vert and j+len(name) < self.n and self.string[i*self.n + j +len(name)] != " "):
			print("RIGHTFIX", (i, j+len(name), True), (i, j+len(name), False), letter)
			self.ijvertPairs[self.string[i*self.n + j + len(name)]].discard((i, (j+len(name)), True))
			self.ijvertPairs[self.string[i*self.n + j + len(name)]].discard((i, (j+len(name)), False))
		'''

		insertTime += time.time() - x
		return self


	def getScore(self, string = None):
		# Function to find score of puzzle so that we print the best puzzle
		if(string is None): string = self.string
		score = 0
		min_row = self.n
		max_row = -1
		min_col = self.n
		max_col = -1
		for i in range(self.n):
			for j in range(self.n):
				ijscore = 0
				letter = string[i*self.n+j]
				if(letter != " "):
					# If the letter is part of a vertical word
					if((i>0 and string[(i-1)*self.n+j] != " ") or (i<self.n-1 and string[(i+1)*self.n+j] != " ")):
						ijscore += 1
					# If the letter is part of a horizontal word
					if((j>0 and string[i*self.n+j-1] != " ") or (j<self.n-1 and string[i*self.n+j+1] != " ")):
						ijscore += 1
					# Update dimensions of puzzle
					if(i < min_row): min_row = i
					if(i > max_row): max_row = i
					if(j < min_col): min_col = j
					if(j > max_col): max_col = j
				if(ijscore == 2):
					firstacross = False
					# If letter is irst letter across
					if((j == 0 or string[i*self.n+j-1] == " ") and j<self.n-1 and string[i*self.n+j+1] != " "):
						firstacross = True
						ijscore += 2
					# If letter is irst letter down
					if((i == 0 or string[(i-1)*self.n+j] == " ") and i<self.n-1 and string[(i+1)*self.n+j] != " "):
						ijscore += 2
						if(firstacross):
							ijscore += 2
				if(ijscore > 1):
					# Scrabble scoring for connections
					if(letter in ["d", "g"]): ijscore += 1
					elif(letter in ["b", "c", "m", "p"]): ijscore += 2
					elif(letter in ["f", "h", "v", "w", "y"]): ijscore += 3
					elif(letter == "k"): ijscore += 4
					elif(letter in ["j", "x"]): ijscore += 7
					elif(letter in ["q", "z"]): ijscore += 9
				score += ijscore
		if(score > 0):
			# Reward puzzles that can be created in less than nxn
			score += (10*min_row + 10*min_col + 10*(self.n-1-max_row) + 10*(self.n-1-max_col))
		return score

	def retime(self, result = False):
		# Retime puzzle, if necessary
		self.seconds += (time.time() - self.last_time)
		self.last_time = time.time()
		if(result):
			self.result_seconds = 0
		else:
			self.result_seconds += (time.time() - self.result_last_time)
		self.result_last_time = time.time()
		return self


	def solve(self, index = 0, solutions = [], regenerate = False):
		global solveCalls # Number of times we find a new solution
		if(hash(self.string) in self.strings and self.string != " "*self.n*self.n):
			return solutions
		solveCalls += 1
		self.strings.add(hash(self.string))

		# If we have an incomplete puzzle but find a puzzle with more names used
		if(len(self.unusedNames) > 0 and self.mostUsedNames < len(self.usedNames)):
			print("Best solution found so far!")
			self.printPuzzles()
			score = self.getScore()
			usedNames, unusedNames = len(self.usedNames), len(self.unusedNames)
			print("SCORE: " + str(score))
			print("NAMES: " + str(usedNames) + "/" + str(usedNames + unusedNames))
			print("UNUSED NAMES: " + str(self.unusedNames))
			if(self.clock): 
				print("SECONDS: " + str(self.seconds))
				self.retime(True)
			print(" ")
			self.bestScore = score
			self.bestString = self.string
			self.mostUsedNames = len(self.usedNames)
		
		# If we have incomplete puzzle but find a puzzle with as many names
		elif(len(self.unusedNames) > 0 and self.mostUsedNames == len(self.usedNames)):
			score = self.getScore()
			# Check if puzzle has a greater score
			if(score > self.bestScore):
				print("Best solution found so far!")
				self.printPuzzles()
				usedNames, unusedNames = len(self.usedNames), len(self.unusedNames)
				print("SCORE: " + str(score))
				print("NAMES: " + str(usedNames) + "/" + str(usedNames + unusedNames))
				print("UNUSED NAMES: " + str(self.unusedNames))
				if(self.clock): 
					print("SECONDS: " + str(self.seconds))
					self.retime(True)
				print(" ")
				self.bestScore = score
				self.bestString = self.string

		# If we DO have a complete puzzle
		if(len(self.unusedNames) == 0):
			score = self.getScore()
			# If we find another complete puzzle that is better
			if(score > self.bestScore and self.mostUsedNames == len(self.usedNames)):
				print("Better solution found!")
				self.printPuzzles()
				usedNames, unusedNames = len(self.usedNames), len(self.unusedNames)
				print("SCORE: " + str(score))
				print("NAMES: " + str(usedNames) + "/" + str(usedNames + unusedNames))
				print("UNUSED NAMES: " + str(self.unusedNames))
				if(self.clock): 
					print("SECONDS: " + str(self.seconds))
					self.retime(True)
				print(" ")
				self.bestScore = score
				self.bestString = self.string

			# If this is our first complete puzzle
			elif(self.mostUsedNames <  len(self.usedNames)):
				print("Solution found!")
				self.printPuzzles()
				usedNames, unusedNames = len(self.usedNames), len(self.unusedNames)
				print("SCORE: " + str(score))
				print("NAMES: " + str(usedNames) + "/" + str(usedNames + unusedNames))
				print("UNUSED NAMES: " + str(self.unusedNames))
				if(self.clock): 
					print("SECONDS: " + str(self.seconds))
					self.retime(True)
				print(" ")				
				self.bestScore = score
				self.bestString = self.string
				self.mostUsedNames = len(self.usedNames)
			#else:
				#print("Solution found!")
			
			solutions.append(self.string)
			return solutions

		else:
			if(index == 0): names = [self.unusedNames[0]]
			else: names = self.unusedNames.copy()
			for name in names:

				if(self.clock):
					self.retime()
					# If we've reached maximum time
					if(self.seconds > self.how_long): break
					# If it's time to regenerate
					elif(self.result_seconds > self.switch_time):
						self.retime(True)
						#solutions = self.solve(solutions = solutions, regenerate = True)
						if(self.print_regenerate): print("REGENERATE", self.seconds)
						self.break_the_loop = True
					else: self.break_the_loop = False

				# If we're regenerating
				if(self.clock and self.break_the_loop and index>0):  
					self.strings.discard(hash(self.string))
					return solutions

				else:
					ijvertPairs = self.ijvertPairsList(name)
					for i, j, vert in ijvertPairs:
						old_string = self.string
						# Check if we needed to regenerate from a puzzle generated in this loop 
						if(self.clock and self.break_the_loop and index>0): 
							self.strings.discard(hash(self.string))
							return solutions
						self.insert(i, j, name, vert)
						# If the insert worked
						if(old_string != self.string):
							next_solutions = self.solve(index+1, solutions)
							if(len(next_solutions) > len(solutions)):
								solutions = next_solutions
							else:
								self.unusedNames.append(name)
								self.usedNames.remove(name)
								new_string = self.string
								self.string = old_string
								self.uninsert(i, j, vert, name, len(name), new_string)


		if(index == 0): 
			if(self.clock):
				while(self.break_the_loop):
					# Reset string, names, and ijverts for regeneration
					self.string = " "*self.n*self.n
					self.unusedNames = sorted(sorted(self.usedNames + self.unusedNames), key = len, reverse = True)
					self.usedNames = []
					self.strings.discard(hash(self.string))
					self.ijvertPairs = dict()
					for p in range(97, 123): self.ijvertPairs[chr(p)] = set()
					solutions = self.solve(solutions = solutions, regenerate = True)
				
				more_strings = len(self.strings)
				# As of right now, regeneration may make some puzzles impossible to reach
				# So wew keep running the algorithm until we run out of time
				while(self.seconds < self.how_long and more_strings > 0):
					self.strings = set()
					self.string = " "*self.n*self.n
					self.unusedNames = sorted(sorted(self.usedNames + self.unusedNames), key = len, reverse = True)
					self.usedNames = []
					self.ijvertPairs = dict()
					for p in range(97, 123): self.ijvertPairs[chr(p)] = set()
					self.empty = True
					solutions = self.solve(solutions = solutions, regenerate = True)
					prev_length = len(self.all_strings)
					self.all_strings = self.all_strings.union(self.strings)
					more_strings = len(self.all_strings) - prev_length
					print(str(more_strings) + " MORE STRINGS FOUND")

			else: self.all_strings = self.strings
			
			# Print data about time and calls
			print("Number of Puzzle Combos Found: ", len(self.all_strings))
			global the_time
			new_time = time.time() - the_time
			print("ijvertPairsList time: " + str(ijvertPairsListTime/(new_time)))
			print("crosswordNotBlocked time: " + str(crosswordNotBlockedTime/(new_time)))
			print("unijvert time: " + str(unijvertTime/(new_time)))
			print("updateijvert time: " + str(updateijvertTime/(new_time)))
			print("insert time: " + str(insertTime/(new_time)))
			print(" ")
			print("ijvertPairsList calls: " + str(ijvertPairsListCalls) + " " + str(ijvertPairsListTime/ijvertPairsListCalls))
			print("crosswordNotBlocked calls: " + str(crosswordNotBlockedCalls) + " " + str(crosswordNotBlockedTime/crosswordNotBlockedCalls))
			print("unijvert calls: " + str(unijvertCalls) + " " + str(unijvertTime/unijvertCalls))
			print("updateijvert calls: " + str(updateijvertCalls) + " " + str(updateijvertTime/updateijvertCalls))
			print("insert calls: " + str(insertCalls) + " " + str(insertTime/insertCalls))
			print("solve calls: " + str(solveCalls))

		return solutions


names = ["taylorswift", "chuckberry", "muhammadali", "neilarmstrong", "isaacnewton",
         "oprahwinfrey", "suebird", "jackiechan", "whitneyhouston", "carlossantana"]

the_crossword = Crossword(15, names)#, how_long = 30, switch_time = 5, print_regenerate = True)#, how_long = 60*60*18, switch_time = 10)
print("TIME: ", time.time() - the_time)
