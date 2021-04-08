import ELO, EPL, FL1, GPL, TSL, ISA, LLA, NBA, NPL, PPL, NFL, BPL, ECL, MLM, UCL, DSL, EUL, AAL, FDA, LLT, MMA, NHL, MLB


def getPicks():
    try:
        NBA.run()
    except:
        print('NBA failed to run')
    try:
        MLB.run()
    except:
        print('MLB failed to run')
    try:
        ELO.run()
    except:
        print('ELO failed to run')
    try:
        NHL.run()
    except:
        print('NHL failed to run')
    try:
        NFL.run()
    except:
        print('NFL failed to run')
    try:
        EPL.run()
    except:
        print('EPL failed to run')
    try:
        GPL.run()
    except:
        print('GPL failed to run')
    try:
        FL1.run()
    except:
        print('FL1 failed to run')
    try:
        TSL.run()
    except:
        print('TSL failed to run')
    try:
        ISA.run()
    except:
        print('ISA failed to run')
    try:
        LLA.run()
    except:
        print('LLA failed to run')
    try:
        NPL.run()
    except:
        print('NPL failed to run')
    try:
        PPL.run()
    except:
        print('PPL failed to run')
    try:
        ECL.run()
    except:
        print('ECL failed to run')
    try:
        MLM.run()
    except:
        print('MLM failed to run')
    try:
        UCL.run()
    except:
        print('UCL failed to run')
    try:
        DSL.run()
    except:
        print('DSL failed to run')
    try:
        EUL.run()
    except:
        print('EUL failed to run')
    try:
        LLT.run()
    except:
        print('LLT failed to run')
    try:
        AAL.run()
    except:
        print('AAL failed to run')
    try:
        FDS.run()
    except:
        print('FDS failed to run')
    try:
        MMA.run()
    except:
        print('MMA failed to run')
    return 'Picks Completed'
	
print('All bets are moneyline bets.')
print(getPicks())


	
