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
	try:
		NFL.run()
	except:
		print('No NFL yet')
	try:
		ELO.run()
	except:
		print("No ELO yet")
	try:
		EPL.run()
	except:
		print('No EPL yet')
	try:
		GPL.run()
	except:
		print('No GPL yet')
	try:
		FL1.run()
	except:
		print('No FL1 yet')
	try:
		TSL.run()
	except:
		print('No TSL yet')
	try:
		ISA.run()
	except:
		print('No ISA yet')
	try:
		LLA.run()
	except:
		print('No LLA yet')
	try:
		NPL.run()
	except:
		print('No NPL yet')
	try:
		PPL.run()
	except:
		print('No PPL yet')
	try:
		ECL.run()
	except:
		print('No ECL yet')
	try:
		MLM.run()
	except:
		print('No MLM yet')
	try:
		UCL.run()
	except:
		print('No UCL yet')
	try:
		DSL.run()
	except:
		print('No DSL yet')
	try:
		EUL.run()
	except:
		print('No EUL yet')
	try:
		LLT.run()
	except:
		print('No LLT yet')
	try:
		AAL.run()
	except:
		print('No AAL yet')
	try:
		FDA.run()
	except:
		print('No FDA yet')
	try:
		BPL.run()
	except:
		print('No BPL yet')
	try:
		MMA.run()
	except:
		print('No MMA yet')
	
	return 'Picks Completed'
	
print('All bets are moneyline bets.')
print(getPicks())
