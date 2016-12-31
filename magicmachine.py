import pdb
import os
import sys
from itertools import izip_longest
from collections import defaultdict, deque

class Halt(Exception): pass

class MagicMachine(object):
	def __init__(self):
		self.memory = defaultdict(lambda: 0)
		self.registers = defaultdict(lambda: 0)
		self.stack = deque()
		self.input_buffer = None
		self.autoinput = deque()

	def load(self, program):
		for address, operation in enumerate(program.split(',')):
			self.memory[address] = int(operation)

	def load_bin(self, filename):
		with open(filename, "rb") as f:
			data = f.read()
		data = map(lambda b: ord(b), data)
		itr = iter(data)

		for address, (bit1, bit2) in enumerate(izip_longest(itr, itr)):
			self.memory[address] = bit1 + (bit2 * (2**8))

	def load_autoinput(self, filename):
		with open(filename, "r") as f:
			for line in f:
				self.autoinput.append(line.strip())

	def print_memory(self, start, length):
		for address in xrange(start, start + length):
			print "%d: %d" % (address, self.memory[address])

	def run(self, start_address = 0):
		self.address = start_address

		while self.address < (2 ** 15):
			opnum = self.lookup(self.memory[self.address])
			operation = self.OPERATIONS[opnum]
			argcount = operation.__code__.co_argcount - 1

			opargs = []
			for argn in xrange(argcount):
				self.address += 1
				arg = self.memory[self.address]
				opargs.append(arg)

			try:
				operation(self, *opargs)
				self.address += 1
			except Halt:
				break

	def lookup(self, value):
		if value >= 32776 or value < 0:
			raise ValueError(value)
		elif value >= 32768:
			return self.registers[self.to_register(value)]
		else:
			return value

	def to_register(self, value):
		return value % (2**15)

	OPERATIONS = {}

	def op_halt(self):
		raise Halt()
	OPERATIONS[0] = op_halt

	def op_set(self, a, b):
		# set register <a> to the value of <b>
		self.registers[self.to_register(a)] = self.lookup(b)
	OPERATIONS[1] = op_set

	def op_push(self, a):
		self.stack.append(self.lookup(a))
	OPERATIONS[2] = op_push

	def op_pop(self, a):
		self.op_set(a, self.stack.pop())
	OPERATIONS[3] = op_pop

	def op_eq(self, a, b, c):
		# set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
		val = 1 if self.lookup(b) == self.lookup(c) else 0
		self.op_set(a, val)
	OPERATIONS[4] = op_eq

	def op_gt(self, a, b, c):
		# set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
		val = 1 if self.lookup(b) > self.lookup(c) else 0
		self.op_set(a, val)
	OPERATIONS[5] = op_gt

	def op_jmp(self, a):
		self.address = self.lookup(a) - 1
	OPERATIONS[6] = op_jmp

	def op_jt(self, a, b):
		# if <a> is nonzero, jump to <b>
		if self.lookup(a) != 0:
			self.op_jmp(b)
	OPERATIONS[7] = op_jt

	def op_jf(self, a, b):
		# if <a> is zero, jump to <b>
		if self.lookup(a) == 0:
			self.op_jmp(b)
	OPERATIONS[8] = op_jf

	def op_add(self, a, b, c):
		# assign into <a> the sum of <b> and <c> (modulo 32768)
		val = (self.lookup(b) + self.lookup(c)) % (2**15)
		self.op_set(a, val)
	OPERATIONS[9] = op_add

	def op_mult(self, a, b, c):
		# store into <a> the product of <b> and <c> (modulo 32768)
		val = (self.lookup(b) * self.lookup(c)) % (2**15)
		self.op_set(a, val)
	OPERATIONS[10] = op_mult

	def op_mod(self, a, b, c):
		# store into <a> the remainder of <b> divided by <c>
		val = self.lookup(b) % self.lookup(c)
		self.op_set(a, val)
	OPERATIONS[11] = op_mod

	def op_and(self, a, b, c):
		# stores into <a> the bitwise and of <b> and <c>
		val = self.lookup(b) & self.lookup(c)
		self.op_set(a, val)
	OPERATIONS[12] = op_and

	def op_or(self, a, b, c):
		val = self.lookup(b) | self.lookup(c)
		self.op_set(a, val)
	OPERATIONS[13] = op_or

	def op_not(self, a, b):
		# stores 15-bit bitwise inverse of <b> in <a>
		val = (-self.lookup(b) - 1) % (2**15)
		self.op_set(a, val)
	OPERATIONS[14] = op_not

	def op_rmem(self, a, b):
		# read memory at address <b> and write it to <a>
		val = self.memory[self.lookup(b)]
		self.op_set(a, val)
	OPERATIONS[15] = op_rmem

	def op_wmem(self, a, b):
		# write the value from <b> into memory at address <a>
		val = self.lookup(b)
		self.memory[self.lookup(a)] = val
	OPERATIONS[16] = op_wmem

	def op_call(self, a):
		# write the address of the next instruction to the stack and jump to <a>
		self.stack.append(self.address + 1)
		self.op_jmp(a)
	OPERATIONS[17] = op_call

	def op_ret(self):
		# remove the top element from the stack and jump to it; empty stack = halt
		if len(self.stack) == 0:
			self.op_halt()

		self.op_jmp(self.stack.pop())
	OPERATIONS[18] = op_ret

	def op_out(self, a):
		sys.stdout.write(chr(self.lookup(a)))
	OPERATIONS[19] = op_out

	def op_in(self, a):
		if self.input_buffer is None:
			if len(self.autoinput) > 0:
				command = self.autoinput.popleft()
				print "(auto) > %s" % command
			else:
				command = raw_input("> ")

			self.input_buffer = (c for c in command)

		try:
			char = self.input_buffer.next()
		except StopIteration:
			self.input_buffer = None
			char = "\n"

		self.registers[self.to_register(a)] = ord(char)
	OPERATIONS[20] = op_in

	def op_noop(self):
		pass
	OPERATIONS[21] = op_noop



if __name__ == '__main__':
	mm = MagicMachine()
	mm.load_bin('challenge.bin')
	mm.load_autoinput('autoinput.txt')
	mm.run()


