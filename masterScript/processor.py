import ELO, EPL, NBA, FL1, GPL, NFL, FL2, KHL

def getPicks():
	NBA.run()
	ELO.run()
	EPL.run()
	NFL.run()
	GPL.run()
	FL1.run()
	FL2.run()
	return 'Picks Completed'
	
print('All bets are moneyline bets.')
print(getPicks())


	
