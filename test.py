from objects import *
import matplotlib.pyplot as plt
import numpy as np

x = Variable("x", np.linspace(-10, +10))
f = x**5 + x**2 + 3*x
print(f(x))


A = Matrix([[1, 0], [0, 1]])
B = Matrix([[2, 5], [7, 5]])
print(f(B))

