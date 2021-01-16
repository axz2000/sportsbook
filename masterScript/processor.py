import ELO, EPL, FL1, GPL, FL2, TSL, ISA, LLA, NBA, NPL, PPL, NFL

#KHL

def getPicks():
	print(NBA.run())
	#print(ELO.run()) fix
	print(EPL.run())
	#NFL.run()
	print(GPL.run())
	print(FL1.run())
	print(FL2.run())
	#print(TSL.run()) drop 2nd instance
	print(ISA.run())
	print(LLA.run())
	print(NPL.run())
	print(PPL.run())
	#print(NFL.run()) fix
	return 'Picks Completed'
	
print('All bets are moneyline bets.')
print(getPicks())


	
