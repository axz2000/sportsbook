import ELO, EPL, NBA, FPL, GPL, NFL, KHL

def getPicks():
	NBA.run()
	ELO.run()
	EPL.run()
	NFL.run()
	GPL.run()
	FPL.run()
	KHL.run()
	#not sure why this runs KHL twice
	return 'Picks Completed'
	
print('All bets are moneyline bets.')
print(getPicks())


	
