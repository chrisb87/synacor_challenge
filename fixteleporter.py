reg0 = 4 # 4, 3, 2, 1, 0, (r1 + 1)
reg1 = 1 # 1, 0, 887, 886, 885...
reg7 = 887
stack = []

def confirm():
	if reg0 > 0:
		if reg1 > 0:
			stack.append(reg0)
			reg1 = (reg1 + 32767) % 32768 # -1
			confirm() # what do we return to?
		else:
			reg0 = (reg0 + 32767) % 32768 # -1
			reg1 = reg7
	else:
		reg0 = reg1 + 1
		print reg0
		return # to..?

confirm()
