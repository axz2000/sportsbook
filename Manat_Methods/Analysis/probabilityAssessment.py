import pandas as pd 
import numpy as np 
'''
success = []
data = pd.read_csv('./sportsbook/masterScript/masterUpcoming.csv')
payouts = data['Payouts (per Dollar)'].values
spent = data['Allocation Dollars'].values
maximum = 2**len(payouts)
length = len(list(str(bin(maximum))[2:])) - 1
arg = '0'+str(length)+'b'
for i in range(0,maximum):
	success += [[int(i) for i in list(str(format(i, arg)))]]

works = []
for i in success:
	if np.sum(i*spent*payouts)>np.sum(spent):
		print(i, spent, payouts)
		works.append(1)
	else:
		works.append(0)

print(np.mean(works))
'''
data = pd.read_csv('./historicalLines/todaysLines.csv')
for i in np.unique(data.GameTag):
	mini = 10000
	dfnew = data[data.GameTag == i]
	for j in data.Update:
		dfnewest = dfnew[dfnew.Update == j]
		if np.mean(dfnewest.Odds.values)<mini:
			mini = np.mean(dfnewest.Odds.values)
			print(i, j, np.mean(dfnewest.Odds.values))
			
		else: continue
#print(data)