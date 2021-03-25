import pandas as pd
import numpy as np

record = pd.read_csv('./recordPDOTD.csv')
record['UnitMultiplier'] = [i for  i in record.Odds.values]
record['UntisWon'] = [record.UnitMultiplier.values[i]*record.Units.values[i]*record.Won.values[i] for i in range(len(record))]
print(record)
print(record[record.Won == 0].Units.values, np.sum(record[record.Won == 0].Units.values))
print(record[record.Won == 1].UntisWon.values, np.sum(record[record.Won == 1].UntisWon.values) - np.sum(record[record.Won == 1].Units.values))
print(np.sum(record.UntisWon.values)-np.sum(record[record.Won == 0].Units.values) - -np.sum(record[record.Won == 1].Units.values), '---------')
port = 100
for i in range(len(record.Units.values)):
	wager = port*(record.Units.values[i]/100)
	port += (wager*record.Odds.values[i]*record.Won.values[i] - wager )
	print(port,  wager, wager*record.Odds.values[i]*record.Won.values[i], record.Won.values[i], '--------')