"""
Puzzle: find the shortest path through LAYOUT.
Start at (0,0), end at (3,3).
Cannot return to (0,0), cannot visit (3,3) except as final location.
Expression represented by path must evaluate to 30, computed from left to right
(ignore order of operations).
"""

from Queue import PriorityQueue

LAYOUT = (
	(22, '-', 9, '*'),
	('+', 4, '-', 18),
	(4, '*', 11, '*'),
	('*', 8, '-', 1),
)

def solve():
	"""A* search from (0,0) to (3,3) using cost() as heuristic"""
	pq = PriorityQueue()
	startpath = ((0,0),)
	pq.put((cost(startpath), startpath))

	while not pq.empty():
		_, path = pq.get()

		if path[-1] == (3,3):
			if computevalue(path) == 30:
				# solved!
				return path
			else:
				# (3,3) can only be final location, so no more moves from here
				pass
		else:
			for move in nextmoves(path[-1]):
				newpath = path + (move,)
				pq.put((cost(newpath), newpath))

def cost(path):
	"""length of existing path plus distance to (3,3)"""
	return len(path) + (3 - path[-1][0]) + (3 - path[-1][0])

def computevalue(path):
	"""converts path to expression and computes it left to right"""
	values = map(lambda l: LAYOUT[l[0]][l[1]], path)

	while len(values) > 1:
		e = eval(' '.join(map(str, values[:3])))
		values = [e] + values[3:]

	return values[0]

def nextmoves(loc):
	"""valid next locations from loc"""
	return filter(validmove, (
		(loc[0], loc[1] + 1),
		(loc[0], loc[1] - 1),
		(loc[0] + 1, loc[1]),
		(loc[0] - 1, loc[1]),
	))

def validmove(loc):
	"""loc must be within 4x4 grid and cannot return to origin"""
	return loc != (0, 0) and \
	loc[0] >= 0 and \
	loc[0] <= 3 and \
	loc[1] >= 0 and \
	loc[1] <= 3


if __name__ == "__main__":
	solution = solve()

	for i in xrange(1, len(solution)):
		curr, prev = solution[i], solution[i - 1]
		diff = (curr[0] - prev[0], curr[1] - prev[1])

		print {
			(1,0): 'north',
			(-1,0): 'south',
			(0, 1): 'east',
			(0, -1): 'west',
		}[diff]
