import requests
import urllib.request
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

def tryMatch(i,j):
	return fuzz.token_sort_ratio(str(i), str(j))

def matching(arrayStrOne,arrayStrTwo):
	matches = []
	for i in arrayStrOne:
		attempt = [fuzz.token_sort_ratio(str(i), str(j)) for j in arrayStrTwo]
		#print(attempt)
		matches += [arrayStrTwo[np.argmax(attempt)]]
	return matches

def to_dataframe(listing):
  home, away, scoreH, scoreA = [], [], [], []
  for i in range(len(listing)):
      #print(i%3, listing[i])
      if i%3 ==0:
        home.append(listing[i].lower())
      elif i%3 == 1:
        away.append(listing[i].lower())
      else:
        score = listing[i].split('-')
        #print(score)
        if len(score) ==2:
          scoreH.append(int(score[0].strip()))
          scoreA.append(int(score[1].strip()))
        else:
          scoreH.append(np.NaN)
          scoreA.append(np.NaN)
  gameLog = pd.DataFrame({'gameDate':[i for i in range(len(home))],'Home':home, 'Away':away,'HomeGoals':scoreH,'AwayGoals':scoreA})
  #print(gameLog)
  return gameLog.dropna()
  
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
  
def getOdds(listing):
  bets = []
  for game in listing:
  	for i in game['eventmarketgroups'][0]['markets']:
  		print(i['name'])
  		betName = [game['externaldescription'], i['name']]
  		if i['name'] == 'Money Line':
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
	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/53474.3.json').json()
	boolean = searchingForGame(jsonData_fanduel_epl)
	return boolean

def fetch():
  try:
  	jsonData_fanduel_nba = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/53474.3.json').json() #gives the game id
  except:
  	print('Not a problem, the XHR has been changed for the NBA, go ahead and fix that then run again')
  print(jsonData_fanduel_nba)
  epl = parse_data(jsonData_fanduel_nba)
  print(epl)
  EPL = pd.DataFrame(epl)[['eventname','tsstart','idfoevent.markets']]
  EPL.columns = ['Teams','Date','EventID']
  listing = []
  for i in np.unique(EPL.EventID.values): 
    listing.append((fullSet(i)))
  df = (pd.DataFrame(getOdds(listing)))
  
  df.columns = ['GameName', 'Type', 'HomeTeamandOdds', 'AwayTeamandOdds']
  df = df[df.Type=='Money Line']
  print(df.sort_values(['GameName']))
  probabilities = fetchName()
  print(probabilities, df)
  fighter, odds = [], []
  name, odds = [], []
  for i in range(len(df)):
  	name += [df.HomeTeamandOdds.values[i][0].lower()]
  	name += [df.AwayTeamandOdds.values[i][0].lower()]
  	odds += [df.HomeTeamandOdds.values[i][1]]
  	odds += [df.AwayTeamandOdds.values[i][1]]
  newest = pd.DataFrame({'ID':name,'Odds':odds})
  result = pd.merge(newest, probabilities, on = 'ID')
  Result = (probabilities.set_index('ID').join(newest.set_index('ID'))).reset_index()
  Result['EV'] = [Result.Probabilities.values[i] * Result.Odds.values[i] for i in range(len(Result))]
  Result['Team'] = Result.ID.values
  Result['Probability'] = Result.Probabilities.values
  Result = Result[['Team','Probability','Odds','EV']]
  print(Result.dropna().to_markdown())
  Bet = Result[Result.EV >1.07]
  kelly = [Kelly(Bet.Odds.values[i], Bet.Probability.values[i]) for i in range(len(Bet.Probability.values))]
  #print(len(Bet.Team.values), len(kelly),  len(Bet.Odds.values))
  Betting = pd.DataFrame({'Bet State Chosen':Bet.Team.values, 'Kelly Criterion Suggestion': kelly, 'Payouts (per Dollar)':Bet.Odds.values})
  print(Betting.dropna().to_markdown())
  #Betting.columns = ['Bet State Chosen', 'Kelly Criterion Suggestion', 'Probability Spread','Payouts (per Dollar)']
  return Betting
  
def fetchName(): 

  jsonData_538 = requests.get('https://projects.fivethirtyeight.com/march-madness-api/2021/madness.json').json()
  mens = jsonData_538['forecasts']['mens']['current_run']['teams']
  teamsToday = [i['team_name'].lower() for i in mens]
  probabilitiesToday = [i['rd4_win'] for i in mens]
  nba = pd.DataFrame({'ID':teamsToday, 'Probabilities':probabilitiesToday})
  return nba

def oddstoPayout(odds,dollarsIn):
  if odds<0:
    multiplier = 1/(abs(odds/100))
    return dollarsIn + dollarsIn*multiplier
  else:
    multiplier = odds/100
    return dollarsIn + dollarsIn*multiplier

def Kelly(oddsDecimal, probability):
  return (oddsDecimal*probability - (1-probability))/oddsDecimal
	
def powerLaw(portfolioAmt,df):
  probs = np.array([(1-(1/i)) for i in df['Payouts (per Dollar)'].values]) #can be used for higher risk tolerance though unused here
  amount = 1/np.prod(probs) #test portfolio constraints
  kelly = df['Kelly Criterion Suggestion'].values
  #spread = df['Probability Spread'].values
  allocation1 = [np.minimum((portfolioAmt*i)*(i/np.sum(kelly)), 0.3*portfolioAmt) for i in kelly] #RISK TOLERANCE ESTABLISHED HERE 
  df['Allocation Dollars'] = allocation1
  print('Total Allocated', np.sum(allocation1).round(decimals=2), 'out of', portfolioAmt)
  df['Allocation Percentage'] = [(i/portfolioAmt) for i in allocation1]
  return df

def gainsLosses(allocation,successes, df, portfolio):
  payouts = df['Payouts (per Dollar)'].values
  prev = np.sum(allocation)
  now = np.sum(np.dot([allocation[i]*payouts[i] for i in range(len(payouts))], successes))
  return [portfolio+(now-prev), prev, now]

def picks():
	result = fetch().round(decimals=2)
	print(result.to_markdown())
	resulting = result[['Bet State Chosen', 'Kelly Criterion Suggestion','Payouts (per Dollar)']]
	resulting['League'] = ['NCAA']*len(resulting['Bet State Chosen'])
	resulting['Date'] = [str(date.today())]*len(resulting['Bet State Chosen'])
	resulting.to_csv(os.getcwd() + '/masterDaily.csv', mode='a', header=False)
	return 'NBA Done'


'''
To do:
-- comment some more stuff and figure out hwo to implement NHl in this exact framework, maybe jsut replace the XHR, but the bettting is different, run seperately?
-- add over under, period bets, make the names for tie more clear if possible
-- make tree structure easy to implement

Notes:
-- Works after 0300, day of
'''
def run():
	if gameToday():
		return picks()
	else:
		return ('No NCAA games today.')

