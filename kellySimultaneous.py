from sympy import *
import numpy as np
import math
import sympy
from sympy.abc import n


f, i = symbols("f i")
e, i = symbols("e i")


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

array = [0.99,0.6, 0.9]
arrayP = [1/i + 0.1 for i in array]
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

print(chunk, leading)

for one in range(len(chunk)):
	equation = []
	for two in range(len(chunk[one])):
		equation += [leading[one]*chunk[one][two]*Indexed('f',two)]
	print(equation)

'''	
f = IndexedBase('f')
array = IndexedBase('array')
arrayed = np.array([3,2,1,0])
s = Sum(f[n]**2 * Indexed('array',n), (n, 0, 3)).doit()
print(s)
fx = lambdify(array, s)
print(fx(arrayed))'''

x, i = symbols("x i")
y= symbols("y")
s = Sum(y*Indexed('x',i),(i,0,3)).doit()
print(s)
f = lambdify(x, s)
print(f)
b = np.array(leading)
print(b)
print(f(b))


#s = Sum((Indexed('p',i)*sympy.log(1+Indexed('z',i)*Indexed('crit',i)),(i,0,k))

'''
x, i = symbols("x i")
y, i = symbols("y i")
z, i = symbols("z i")
crit = symbols("crit")

s = Sum(Product(Indexed('p',i),(i,0,k))*sympy.log(1+))
s = Sum((Indexed('p',i)*sympy.log(1+Indexed('z',i)*Indexed('crit',i)),(i,0,k))

prod = []
for i in range(k):
	prod += 


s = Sum((Indexed('x',i)*Indexed('y',i))*sympy.log(1+Indexed('z',i)*Indexed('crit',i)),(i,0,k))
f = lambdify((x,y), s)

X = np.array([0.9,0.1])
Y = np.array([1/i+ 0.1 for i in X])
Z = np.array([0.9,0.1])

solver = sympy.solve(f(X,Y),crit)
print(solver)



from sympy import *
x, i = symbols("x i")
y, i = symbols("y i")
z, i = symbols("z i")
crit, i = symbols("crit i")
f = 1/sqrt(Sum(x[k]**2, (k, 1, n)))
print(f.diff(x[j]))


eq1 = x**2 + y**2 - 4  # circle of radius 2
eq2 = 2*x + y - 1  # straight line: y(x) = -2*x + 1
solve([eq1, eq2], [x, y])


def function(a,b,c):
	print(a,1+b*c)
	return a*math.log(1+b*c)

fcrit = np.sum([function(X[i],Y[i],solver[-1]) for i in range(len(X)+1)])

print(fcrit)
'''
