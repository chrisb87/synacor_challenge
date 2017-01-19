require 'pqueue'

# y, x
LAYOUT = [
	[22, '-', 9, '*'],
	['+', 4, '-', 18],
	[4, '*', 11, '*'],
	['*', 8, '-', 1],
]

def lookup_location(loc)
	LAYOUT[loc[0]][loc[1]]
end

def compute_value(path)
	values = path.map{ |l| lookup_location(l) }
	puts "\t#{values.join(' ')}"

	while values.length > 1
		e = eval(values[0..2].join(' '))
		values = [e] + values[3..-1]
	end

	puts "\t\t#{values[0]}"
	values[0]
end

def next_moves(loc)
	[
		[loc[0], loc[1] + 1],
		[loc[0], loc[1] - 1],
		[loc[0] + 1, loc[1]],
		[loc[0] - 1, loc[1]],
	].select do |l2|
		l2 != [0,0] && \
		l2.all?{ |c| c >= 0 && c <= 3 }
	end
end

def cost(path)
	# length of existing path, plus distance to [3,3]
	path.length + (3 - path[-1][0]) + (3 - path[-1][1])
end

def solve
	pq = PQueue.new([[[0,0]]]) do |p1, p2|
		cost(p2) <=> cost(p1)
	end

	while pq.length > 0
		path = pq.pop
		puts path.inspect

		if (path[-1] == [3,3])
			return path if compute_value(path) == 30
		else 
			next_moves(path[-1]).each do |nextmove|
				pq << (path + [nextmove])
			end
		end
	end

	puts "no solution found"
end

#solution = solve
solution = [[0, 0], [1, 0], [1, 1], [1, 2], [2, 2], [2, 1], [1, 1], [1, 2], [1, 3], [1, 2], [2, 2], [3, 2], [3, 3]]

1.upto(solution.length - 1) do |i|
	curr, prev = solution[i], solution[i - 1]

	puts case
	when curr[0] > prev[0]
		'north'
	when curr[0] < prev[0]
		'south'
	when curr[1] > prev[1]
		'east'
	when curr[1] < prev[1]
		'west'
	end
end
