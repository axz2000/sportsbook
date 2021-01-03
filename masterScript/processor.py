import ELO, EPL, NBA, FPL, GPL, NFL

def getPicks():
	NBA.run()
	ELO.run()
	EPL.run()
	NFL.run()
	GPL.run()
	FPL.run()
	return 'Picks Completed'
	
print('All bets are moneyline bets.')
print(getPicks())


	
