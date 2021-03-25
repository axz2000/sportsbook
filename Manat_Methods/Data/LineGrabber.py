import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import math
from scipy.stats import poisson, expon
from pandas import json_normalize
from functools import reduce
import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import os
import tabulate
import time
from git import Repo

def pushing():
	repo_dir = 'historicalbettinglinesNBA'
	repo = Repo(repo_dir)
	file_list = ['Lines'+str(str(datetime.now())[:10])+'.csv']
	commit_message = 'Add new line data'
	repo.index.add(file_list)
	repo.index.commit(commit_message)
	origin = repo.remote('origin')
	origin.push()
	return 'Done'

def get_sections():
	jsonData_fanduel_nba = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/63747.3.json').json()
	return parse_data_sectionCount(jsonData_fanduel_nba)
	
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

def parse_data_sectioncount(jsonData):
    results_df = pd.DataFrame()
    for alpha in jsonData['events']:
    	timeStart = alpha['tsstart'][-8:-6]
    	hourNow = datetime.now().hour +1
    	timeSleep = 60*15
    	seconds = (int(timeStart)-int(hourNow))*60*60
    	sections = int(seconds/timeSleep)
    	break
    return sections

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
  		#print(i['name'])
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
	return today == gameday

def searchingForFirst(jsonData):
	results_df = pd.DataFrame()
	alpha = jsonData['events'][0]
	gameday = alpha['tsstart'][-8:-6]
	nowish = datetime.now().hour
	return int(nowish) < int(gameday)

def gameFirst():
	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/63747.3.json').json()
	boolean = searchingForFirst(jsonData_fanduel_epl)
	return boolean
	
def gameToday():
	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/63747.3.json').json()
	boolean = searchingForGame(jsonData_fanduel_epl)
	return boolean

def fetch(counting):
  try:
  	jsonData_fanduel_nba = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/63747.3.json').json() #gives the game id
  except:
  	print('Not a problem, the XHR has been changed for the NBA, go ahead and fix that then run again')
  epl = parse_data(jsonData_fanduel_nba)
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
  Strings = 'Odds'+str(counting)
  calling = pd.DataFrame({'Team':teams, Strings:lines})
  csvName = './Lines' + str(datetime.now())[:10] + '.csv'
  try:
  	precalled = pd.read_csv(csvName)
  	precalled = precalled.set_index('Team').join(calling.set_index('Team'))
  	precalled.to_csv(csvName)
  except:
  	calling.to_csv(csvName)
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
	counter = 0
	while True:
		time.sleep(7)
		if gameFirst() and gameToday():
			success = fetch(counter)
			github = pushing()
			counter += 1
			print(counter)
		else:
			counter = 0

print(run())


