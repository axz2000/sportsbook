from sympy import *
import numpy as np
import math
import sympy
from sympy.abc import n


def switching(p,b):
	if b<1:
		return 1-p
	else:
		return p

def binary(o,b):
	if b<1:
		return -1
	else:
		return o

array = [0.669, 0.549, 0.373, 0.347, 0.1, 0.1, 0.1, 0.2, 0.3]
arrayP = [1.75, 2.25, 3.6, 3.3, 1.1, 10.1, 111.1, 1.2, 300]
k = len(array) - 1

maximum = 2**len(array)
length = len(list(str(bin(maximum))[2:])) - 1
arg = '0'+str(length)+'b'
success = []
for i in range(0,maximum):
	success += [[int(i) for i in list(str(format(i, arg)))]]
b = np.array(success)

b[b<1]=-1

leading = []
for i in range(len(b)):
	leading += [np.prod([switching(array[j],b[i][j]) for j in range(len(b[i]))])]

chunk = []
for i in range(len(b)):
	chunk += [[binary(arrayP[j],b[i][j]) for j in range(len(b[i]))]]

for one in range(len(chunk)):
	equation = []
	for two in range(len(chunk[one])):
		equation += [leading[one]*chunk[one][two]*Indexed('f',two)]


p = array
k = len(p)-1
kp = len(p)**2 -1
crit = symbols("crit")
p, i = symbols("p i", positive = True)
y, i = symbols("y i")
f, i = symbols("f i", positive = True, real = True)
b, i = symbols("b i", positive = True)

	
s = 1 + Sum(Indexed('f',i)*Indexed('b',i),(i,0,k)).doit()
sl = sympy.log(s)
slp = 0


for j in range(len(chunk)):
	slp += leading[j]*sl.subs({Indexed('b',i): chunk[j][i] for i in range(len(array))})

print(slp)

system = []
for i in range(len(array)):
	system += [sympy.diff(slp, Indexed('f',i))]

print(system)

s = -1*slp
fx = lambdify(f, s)


import numpy as np
from scipy.optimize import fmin
import math

for i in range(10):
	try:
		print(fmin(fx,[i/10]*len(array)))
		break
	except:
		print('None found')

'''
f = lambdify((x,y), sss)

print(s.doit())
X = np.array([0.9,0.99])
Y = np.array([1.2,1.3])
Z = np.array([0.9,0.1])
print(f(X,Y))
solver = sympy.solve(f(X,Y),crit)
print(solver)'''