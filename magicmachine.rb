require 'pry'

class MagicMachine
	class Halt < StandardError; end

	OPCODES = %w{
		halt set push pop eq gt jmp jt jf add mult mod and or not 
		rmem wmem call ret out in noop
	}

	ADMIN_COMMANDS = [
		'quit', 'registers', 'set register', 'fix teleporter'
	]

	attr_reader :memory, :registers, :stack

	def initialize()
		@address = 0
		@memory = Array.new(2**15){ 0 }
		@registers = Array.new(8){ 0 }
		@stack = []
		@input_buffer = []
		@autoinput = []
	end

	def inspect
		to_s
	end

	def load_bin(filename)
		next_address = 0

		File.open(filename) do |file|
			until file.eof?
				next_vals = file.read(2).bytes.map{ |b| b.ord }
				@memory[next_address] = next_vals[0] + (next_vals[1] * 2**8)
				next_address += 1
			end
		end

		next_address
	end

	def load_autoinput(filename)
		@autoinput = File.open(filename).readlines
	end

	def run(start_address = 0)
		@address = start_address

		while @address < @memory.length
			opaddr = @address
			opnum = @memory[@address]
			opname = OPCODES[opnum]
			operation = method("op_#{opname}")
			opargs = []

			operation.arity.times do
				@address += 1
				opargs << @memory[@address]
			end

			begin
				ret = operation.call(*opargs)
				@address += 1 if ret != 'jmp'
			rescue Halt
				break
			end
		end
	end

	def to_register(value)
		value % (2**15)
	end

	def resolve(value)
		if value >= (2**15)
			@registers[to_register(value)]
		else
			value
		end
	end

	def admin_quit
		op_halt
	end

	def admin_registers
		puts @registers.inspect
	end

	def admin_set_register(regnum, val)
		op_set(regnum.to_i, val.to_i)
	end

	def admin_fix_teleporter
		@registers[7] = 5
		@memory[6027...6030] = [1, 32769, 32775]
		@memory[6030...6034] = [9, 32768, 32769, 1]
	end

	def op_halt
		raise Halt
	end

	def op_set(a, b)
		@registers[to_register(a)] = resolve(b)
	end

	def op_push(a)
		@stack << resolve(a)
	end

	def op_pop(a)
		op_set(a, @stack.pop)
	end

	def op_eq(a, b, c)
		val = resolve(b) == resolve(c) ? 1 : 0
		op_set(a, val)
	end

	def op_gt(a, b, c)
		val = resolve(b) > resolve(c) ? 1 : 0
		op_set(a, val)
	end

	def op_jmp(a)
		@address = resolve(a)
		'jmp'
	end

	def op_jt(a, b)
		op_jmp(b) if resolve(a) != 0
	end

	def op_jf(a, b)
		op_jmp(b) if resolve(a) == 0
	end

	def op_add(a, b, c)
		val = (resolve(b) + resolve(c)) % (2**15)
		op_set(a, val)
	end

	def op_mult(a, b, c)
		val = (resolve(b) * resolve(c)) % (2**15)
		op_set(a, val)
	end

	def op_mod(a, b, c)
		val = resolve(b) % resolve(c)
		op_set(a, val)
	end

	def op_and(a, b, c)
		val = resolve(b) & resolve(c)
		op_set(a, val)
	end

	def op_or(a, b, c)
		val = resolve(b) | resolve(c)
		op_set(a, val)
	end

	def op_not(a, b)
		val = (-resolve(b) - 1) % (2**15)
		op_set(a, val)
	end

	def op_rmem(a, b)
		val = @memory[resolve(b)]
		op_set(a, val)
	end

	def op_wmem(a, b)
		@memory[resolve(a)] = resolve(b)
	end

	def op_call(a)
		@stack << @address + 1
		op_jmp(a)
	end

	def op_ret
		op_halt if @stack.empty?
		op_jmp(@stack.pop)
	end

	def op_out(a)
		print resolve(a).chr
	end

	def op_in(a)
		prompt = "> "

		if @input_buffer.empty?
			command = nil

			while command.nil?
				if @autoinput.empty? || @autoinput[0] == "---\n"
					print prompt
					command = gets
				else
					command = @autoinput.shift

					if command.start_with?('#')
						command = nil
						next
					end

					print "(auto) #{prompt}#{command}"
				end

				ADMIN_COMMANDS.each do |admin_command|
					if command.start_with?(admin_command)
						method_name = "admin_#{admin_command.gsub(' ', '_')}"
						args = command[admin_command.length+1..-1].split
						method(method_name).call(*args)

						command = nil
						break
					end
				end
			end

			@input_buffer = command.split('')
		end

		char = @input_buffer.shift
		op_set(a, char.ord)
	end

	def op_noop
	end

end

if __FILE__ == $0
    mm = MagicMachine.new
    mm.load_bin('challenge.bin')
    mm.load_autoinput('autoinput.txt')
	mm.run
end


