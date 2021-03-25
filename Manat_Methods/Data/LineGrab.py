import requests
import urllib.request
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import math
from pandas import json_normalize
from functools import reduce
import os
import tabulate
import time


def parse_data(jsonData):
    results_df = pd.DataFrame()
    for alpha in jsonData['events']:
        gameday = (alpha['tsstart'][:10])
        if (gameday == str(date.today())):
        	print ('Gathering %s data: %s @ %s' %(alpha['sportname'],alpha['participantname_away'],alpha['participantname_home']))
        	alpha_df = json_normalize(alpha).drop('markets',axis=1)
        	for beta in alpha['markets']:
        		beta_df = json_normalize(beta).drop('selections',axis=1)
        		beta_df.columns = [str(col) + '.markets' for col in beta_df.columns]
        		for theta in beta['selections']:
        			theta_df = json_normalize(theta)
        			theta_df.columns = [str(col) + '.selections' for col in theta_df.columns]
        			temp_df = reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True), [alpha_df, beta_df, theta_df])
        			results_df = results_df.append(temp_df, sort=True).reset_index(drop=True)
	
    return results_df #time right for <7 on prev day

def fullSet(eventID):
  #print(eventID,requests.get('https://sportsbook.fanduel.com//cache/psevent/UK/1/false/'+ str(eventID) + '.json').json())
  return requests.get('https://sportsbook.fanduel.com//cache/psevent/UK/1/false/'+ str(eventID) + '.json').json()

def build(oddsDataFrame,dataInput): #NEEDS WORK !!!!!!!
  betting = []
  for i in range(len(oddsDataFrame.iloc[:,0].values)):
    betName = oddsDataFrame.iloc[:,1].values[i]
    game = oddsDataFrame.iloc[:,0].values[i]
    for i in oddsDataFrame.iloc[i,2:].values:
      if i!=None:
        betting += [betFunction(game, betName,i, GoalsLookup)]
  df = pd.DataFrame(betting).dropna()
  df = df.reset_index()
  df.columns = ['Bet Number','Game','Team','Payout','Type']
  return df
  
def getOdds(listing):
  bets = []
  print(len(listing))
  for game in listing:
  	for i in game['eventmarketgroups'][0]['markets']:
  		print(i['name'])
  		betName = [game['externaldescription'], i['name']]
  		if i['name'] == 'Moneyline':
  			for i in i['selections']:
  				print([i['name'], 1+(i['currentpriceup']/i['currentpricedown'])])
  				betName+=[[i['name'], 1+(i['currentpriceup']/i['currentpricedown'])]] #, i['currenthandicap']
  		bets += [betName]
  return bets

def searchingForGame(jsonData):
	results_df = pd.DataFrame()
	alpha = jsonData['events'][0]
	gameday = alpha['tsstart'][:10]
	today = str(date.today())
	print(today, gameday)
	return today == gameday

def gameToday():
	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/63747.3.json').json()
	boolean = searchingForGame(jsonData_fanduel_epl)
	return boolean

def fetch():
  try:
  	jsonData_fanduel_nba = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/63747.3.json').json() #gives the game id
  except:
  	print('Not a problem, the XHR has been changed for the NBA, go ahead and fix that then run again')
  epl = parse_data(jsonData_fanduel_nba)
  #print(epl)
  EPL = pd.DataFrame(epl)[['eventname','tsstart','idfoevent.markets']]
  EPL.columns = ['Teams','Date','EventID']
  listing = []
  for i in np.unique(EPL.EventID.values): 
    listing.append((fullSet(i)))
  df = (pd.DataFrame(getOdds(listing)))
  df.columns = ['GameName', 'Type', 'HomeTeamandOdds', 'AwayTeamandOdds']
  df = df[df.Type=='Moneyline']
  counter = 0
  teams, game, lines = [],[],[]
  for i in df.GameName:
  	teams.append(df[df.GameName == i].HomeTeamandOdds.values[0][0])
  	teams.append(df[df.GameName == i].AwayTeamandOdds.values[0][0])
  	game.append(counter)
  	game.append(counter)
  	lines.append(df[df.GameName == i].HomeTeamandOdds.values[0][1])
  	lines.append(df[df.GameName == i].AwayTeamandOdds.values[0][1])
  	counter +=1
  Strings = 'Odds'+str(datetime.now())
  calling = pd.DataFrame({'Team':teams, Strings:lines})
  try:
  	precalled = pd.read_csv('./Lines.csv')
  	precalled = precalled.set_index('Team').join(calling.set_index('Team'))
  	precalled.to_csv('./Lines.csv')
  except:
  	calling.to_csv('./Lines.csv')
  return 'Done'

def oddstoPayout(odds,dollarsIn):
  if odds<0:
    multiplier = 1/(abs(odds/100))
    return dollarsIn + dollarsIn*multiplier
  else:
    multiplier = odds/100
    return dollarsIn + dollarsIn*multiplier

'''
To do:
-- comment some more stuff and figure out hwo to implement NHl in this exact framework, maybe jsut replace the XHR, but the bettting is different, run seperately?
-- add over under, period bets, make the names for tie more clear if possible
-- make tree structure easy to implement

Notes:
-- Works after 0300, day of
'''

def run():
	go = True
	while True:
		if gameToday():
			timestamp = 5
			#you need the right time breakdown that is always the same
			try:
				table = fetch()
				go = True
			except:
				if go:
					precalled = pd.read_csv('./Data/Lines.csv')
					precalled.to_csv(os.getcwd() + '/Data/savedLines.csv', mode='a', header=False)
					go = False
				else:
					print('we got continue')
					continue
			if go:
				continue
			else:
				print('we hit the 3 hour sleep')
				time.sleep(60*60*3)	
		else:
			time.sleep(60*60*20)

print(run())

