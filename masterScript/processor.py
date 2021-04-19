import ELO, EPL, FL1, GPL, TSL, ISA, LLA, NBA, NPL, PPL, NFL, BPL, ECL, MLM, UCL, DSL, EUL, AAL, FDA, LLT, MMA, NHL, MLB


def getPicks():
	
	try:
		NBA.run()
	except:
		print('No NBA yet')
	
	try:
		MLB.run()
	except:
		print('No MLB yet')
	
	try:
		NHL.run()
	except:
		print('No NHL yet')

	#NFL.run()
	ELO.run()
	EPL.run()
	GPL.run()
	FL1.run()
	TSL.run()
	ISA.run()
	LLA.run()
	NPL.run()
	#PPL.run()
	ECL.run()
	#MLM.run()
	UCL.run()
	#DSL.run()
	EUL.run()
	LLT.run()
	#AAL.run()
	FDA.run()
	#BPL.run()
	MMA.run()
	
	return 'Picks Completed'
	
print('All bets are moneyline bets.')
print(getPicks())
