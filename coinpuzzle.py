# _ + _ * _^2 + _^3 - _ = 399

# red: 			2
# corroded: 	triangle (3?)
# shiny:		pentagon (5?)
# concave: 		7
# blue:			9

from itertools import permutations

coins = (
	('red', 2),
	('corroded', 3),
	('shiny', 5),
	('concave', 7),
	('blue', 9),
)

def func(a, b, c, d, e):
	return a + b * (c**2) + (d**3) - e

for coinset in permutations(coins):
	values = [val for color, val in coinset]
	result = func(*values)

	if result == 399:
		print [color for color, val in coinset]
		# ['blue', 'red', 'shiny', 'concave', 'corroded']
