import pdb
import os
import sys
from itertools import izip_longest
from collections import deque

class MagicMachine(object):
	class Halt(Exception): pass

	OPCODES = ('halt', 'set', 'push', 'pop', 'eq', 'gt', 'jmp', 'jt', 'jf', 
		'add', 'mult', 'mod', 'and', 'or', 'not', 'rmem', 'wmem', 'call', 
		'ret', 'out', 'in', 'noop')

	ADMIN_COMMANDS = ('memdump')

	def __init__(self):
		self.memory = [0 for _ in xrange(2**15)]
		self.registers = [0 for _ in xrange(8)]
		self.stack = deque()
		self.input_buffer = None
		self.autoinput = deque()

		self.operations = []
		for opcode in self.OPCODES:
			op = getattr(self, "op_%s" % opcode)
			self.operations.append((op, op.__code__.co_argcount - 1))

	def load_bin(self, filename):
		with open(filename, "rb") as f:
			data = f.read()

		itr = iter(data)
		for address, (bit1, bit2) in enumerate(izip_longest(itr, itr)):
			self.memory[address] = ord(bit1) + (ord(bit2) * (2**8))

	def load_autoinput(self, filename):
		with open(filename, "r") as f:
			for line in f:
				self.autoinput.append(line.strip())

	def memdump(self, filename = None):
		n = 0

		if filename is None:
			while True:
				filename = "memdumps/memdump_%04d.txt" % n
				if os.path.exists(filename):
					n += 1
				else:
					break
		else:
			filename = "memdumps/%s.txt" % filename

		with open(filename, 'w') as f:
			f.write("Registers:\n\n")
			for n in xrange(8):
				f.write("%d: %d\n" % (n, self.registers[n]))

			f.write("\nStack:\n\n")
			if len(self.stack) == 0:
				f.write("(empty)")
			else:
				for s in self.stack:
					f.write("%s\n" % s)

			f.write("\n\nMemory:\n\n")
			for n in xrange(2**15):
				f.write("%05d: %d\n" % (n, self.memory[n]))

	def run(self, start_address = 0):
		self.address = start_address

		while self.address < (2 ** 15):
			opnum = self.memory[self.address]
			operation, argcount = self.operations[opnum]

			opargs = []
			for _ in xrange(argcount):
				self.address += 1
				arg = self.memory[self.address]
				opargs.append(arg)

			try:
				result = operation(*opargs)

				if result != 'jmp':
					self.address += 1

			except self.Halt:
				print "HALT at %d" % self.address
				break

	def lookup(self, value):
		if value >= (2**15 + 8) or value < 0:
			raise ValueError(value)
		elif value >= (2**15):
			return self.registers[self.to_register(value)]
		else:
			return value

	def to_register(self, value):
		return value % (2**15)

	def op_halt(self):
		raise self.Halt()

	def op_set(self, a, b):
		self.registers[self.to_register(a)] = self.lookup(b)

	def op_push(self, a):
		self.stack.append(self.lookup(a))

	def op_pop(self, a):
		self.op_set(a, self.stack.pop())

	def op_eq(self, a, b, c):
		val = 1 if self.lookup(b) == self.lookup(c) else 0
		self.op_set(a, val)

	def op_gt(self, a, b, c):
		val = 1 if self.lookup(b) > self.lookup(c) else 0
		self.op_set(a, val)

	def op_jmp(self, a):
		self.address = self.lookup(a)
		return 'jmp'

	def op_jt(self, a, b):
		if self.lookup(a) != 0:
			return self.op_jmp(b)

	def op_jf(self, a, b):
		if self.lookup(a) == 0:
			return self.op_jmp(b)

	def op_add(self, a, b, c):
		val = (self.lookup(b) + self.lookup(c)) % (2**15)
		self.op_set(a, val)

	def op_mult(self, a, b, c):
		val = (self.lookup(b) * self.lookup(c)) % (2**15)
		self.op_set(a, val)

	def op_mod(self, a, b, c):
		val = self.lookup(b) % self.lookup(c)
		self.op_set(a, val)

	def op_and(self, a, b, c):
		val = self.lookup(b) & self.lookup(c)
		self.op_set(a, val)

	def op_or(self, a, b, c):
		val = self.lookup(b) | self.lookup(c)
		self.op_set(a, val)

	def op_not(self, a, b):
		val = (-self.lookup(b) - 1) % (2**15)
		self.op_set(a, val)

	def op_rmem(self, a, b):
		val = self.memory[self.lookup(b)]
		self.op_set(a, val)

	def op_wmem(self, a, b):
		val = self.lookup(b)
		self.memory[self.lookup(a)] = val

	def op_call(self, a):
		self.stack.append(self.address + 1)
		return self.op_jmp(a)

	def op_ret(self):
		if len(self.stack) == 0:
			self.op_halt()
		return self.op_jmp(self.stack.pop())

	def op_out(self, a):
		sys.stdout.write(chr(self.lookup(a)))

	def op_in(self, a):
		prompt = "> "

		if self.input_buffer is None:
			if len(self.autoinput) > 0:
				command = self.autoinput.popleft()
				print "(auto) %s%s" % (prompt, command)
			else:
				command = raw_input(prompt)

				while command.split()[0] in self.ADMIN_COMMANDS:
					split = command.split()
					getattr(self, split[0])(*split[1:])
					command = raw_input(prompt)

			self.input_buffer = (c for c in command)

		try:
			char = self.input_buffer.next()
		except StopIteration:
			self.input_buffer = None
			char = "\n"

		self.registers[self.to_register(a)] = ord(char)

	def op_noop(self):
		pass



if __name__ == '__main__':
	mm = MagicMachine()
	mm.load_bin('challenge.bin')
	mm.load_autoinput('autoinput.txt')
	mm.run()


