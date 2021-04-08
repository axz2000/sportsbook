from sympy import *
import numpy as np
import math
import sympy
from sympy.abc import n
import pandas as pd
from scipy.optimize import fmin
import math


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

def reverseKelly(payout, kelly):
	return( ((kelly * payout) + 1)/(payout + 1) )

def run():	
	csvs = pd.read_csv('./masterUpcoming.csv')
	array = [reverseKelly(csvs['Payouts (per Dollar)'].values[i],csvs['Kelly Criterion Suggestion'].values[i]) for i in range(len(csvs))] #probability that the stock will go up
	arrayP = [i - 1 for i in csvs['Payouts (per Dollar)'].values]
	print(array, arrayP, 'Check your inputs')
	k = len(array) - 1
	if k ==0:
		return csvs['Kelly Criterion Suggestion'].values * 1/3

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

	counter = 0
	for i in range(10):
		try:
			counter += 1
			finished = (fmin(fx,[i/10]*len(array)))
		
			if counter == 2:
				csvs['Allocation Percentage'] = finished*1/3
				csvs.to_csv('./newKellyFraction.csv')
				return finished
		except:
			print('None found')
