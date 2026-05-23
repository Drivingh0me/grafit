import numpy as np

usr_func = "2 * x + a"

# def func(x, a, func_txt: str):
# 	return eval(func_txt)

# Restrict variables to prevent malicous function formation
class Function:
	def __init__(self, function: str, numvar: int):
		self.func = lambda x, a: eval(function)
		self.numvar = numvar

my_func = Function(usr_func, 2)
print(f"numvar: {my_func.numvar}")

y = my_func.func(1, 2)

print(f"y = {y}")
