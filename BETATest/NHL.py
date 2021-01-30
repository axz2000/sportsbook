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

#Team Name SetUp
basicTeams = requests.get('https://statsapi.web.nhl.com/api/v1/teams')
abbrevArray, IDArray , Name= [basicTeams.json().get("teams")[i].get("abbreviation") for i in range(len(basicTeams.json().get("teams")))], [basicTeams.json().get("teams")[i].get('id') for i in range(len(basicTeams.json().get("teams")))],[basicTeams.json().get("teams")[i].get('name') for i in range(len(basicTeams.json().get("teams")))]
teamID = pd.DataFrame({'ID':IDArray, 'Abbr':abbrevArray, 'Name':Name})

#_____________________________________________FUNCTIONS_____________________________________________________

#gets the addresses for the various json files
def parse_data(jsonData):
    results_df = pd.DataFrame()
    for alpha in jsonData['events']:
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

    return results_df

def fullSet(eventID):
  return requests.get('https://sportsbook.fanduel.com//cache/psevent/UK/1/false/'+ str(eventID) + '.json').json()

def getOdds(listing):
  bets = []
  for game in listing:
    for i in game['eventmarketgroups'][0]['markets']:
      betName = [game['externaldescription'], i['name']]
      for i in i['selections']:
        betName+=[[i['name'], (i['currentpriceup']/i['currentpricedown'])]]
      bets += [betName]
  return bets

def build(oddsDataFrame,GoalsLookup):
  betting = []
  for i in range(len(oddsDataFrame.iloc[:,0].values)):
    betName = oddsDataFrame.iloc[:,1].values[i]
    game = oddsDataFrame.iloc[:,0].values[i]
    for i in oddsDataFrame.iloc[i,2:].values:
      if i!=None:
        betting += [betFunction(game, betName,i, GoalsLookup)]
  df = pd.DataFrame(betting).dropna()
  df = df.reset_index()
  print(df)
  df.columns = ['Bet Number','Game','Team','DecimalOdds','Type']
  return df

def fetch(LU):
  jsonData_fanduel_nhl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/56572.3.json').json() #gives the game id
  nhl = parse_data(jsonData_fanduel_nhl)
  NHL = pd.DataFrame(nhl)[['eventname','tsstart','idfoevent.markets']]
  NHL.columns = ['Teams','Date','EventID']
  listing = []
  for i in np.unique(NHL.EventID.values): #pulls all odds for the specified game
    listing.append((fullSet(i)))
  print(pd.DataFrame(getOdds(listing))[[1]])
  return build(pd.DataFrame(getOdds(listing)),LU)

def Poisson(mu,discreteStep):
  poiArray = [poisson(mu).pmf(x) for x in range(discreteStep)]
  poiArray.append(1-sum(poiArray))
  return poiArray

def poissonMatrix(avGoalsHome,avGoalsAway):
  Home = np.array(Poisson(avGoalsHome,7))
  Away = np.array(Poisson(avGoalsAway,7)).reshape(len(Home),1)
  return Away*Home #return np matrix

def oddstoPayout(odds,dollarsIn):
  if odds<0:
    multiplier = 1/(abs(odds/100))
    return dollarsIn + dollarsIn*multiplier
  else:
    multiplier = odds/100
    return dollarsIn + dollarsIn*multiplier

def expectedValue(payout,probability):
  return payout*probability

def bet(expectedValue,Team):
  if expectedValue>1:
    return Team
  else:
    return None

def Kelly(oddsDecimal, probability):
  return (oddsDecimal*probability - (1-probability))/oddsDecimal

#The meat of the code, this is the data reconstruction from the NHL APIs there is a date issue but this can be resolved with sme work - has been resolved
def dailyGames(daysBack):
  lookBackTimeFrame = daysBack
  i = str(datetime.date(datetime.now()))
  threeWeeksPrior = str(datetime.date(datetime.now() - timedelta(days=lookBackTimeFrame)))
  return requests.get('https://statsapi.web.nhl.com/api/v1/schedule?startDate=' + threeWeeksPrior + '&endDate=' + i ).json().get('dates')

def dailyGamesGetDay(jsonArray,daysBack):
  return jsonArray[-(daysBack)]

def reconstructGameLog(daysBack):
  LookBack = []
  gamesPlayed = dailyGames(daysBack)
  for i in range(1,daysBack):
    try:
      gameList = dailyGamesGetDay(gamesPlayed,i).get('games')
      #print(i,gameList)
      for i in range(len(gameList)):
        gameLog = gameList[i].get('teams')
        
        #Features
        if (gameList[i].get('status').get('abstractGameState') == 'Final'):
          gameID = gameList[i].get('gameDate')
          Home = gameLog.get('home').get('team').get('id')
          Away = gameLog.get('away').get('team').get('id')
          HomeGoals = gameLog.get('home').get('score')
          AwayGoals = gameLog.get('away').get('score')

          HomeShots = gameLog.get('home').get('shots')
          AwayShots = gameLog.get('away').get('shots')
          #HomePDO = (HomeGoals/HomeShots)+(AwayShots/AwayGoals)
          #AwayPDO = (AwayGoals/AwayShots)+(HomeShots/HomeGoals)

          #HomeGoals = HomeGoals/HomePDO
          #AwayGoals = AwayGoals/AwayPDO

          LookBack += [[gameID, Home, Away, HomeGoals, AwayGoals]]
    except:
      continue

  #construct a DataFrame
  gameLogs = pd.DataFrame(LookBack)
  gameLogs.columns = ['gameDate', 'Home', 'Away', 'HomeGoals', 'AwayGoals']
  gameLogs = gameLogs.sort_values('gameDate')
  #print(gameLogs)
  return gameLogs

def teamReconstruction(id,LogTable):
  LogTableH = LogTable[LogTable.Home ==id][['gameDate','HomeGoals']]
  LogTableA = LogTable[LogTable.Away ==id][['gameDate','AwayGoals']]
  #print(LogTableH,LogTableA,id)
  LogTables = LogTableH.append(LogTableA).sort_values('gameDate',ascending=False).replace(np.NaN,0)
  goalScored = [int(i) for i in np.array(LogTables.HomeGoals+LogTables.AwayGoals)]
  return np.array(goalScored)

def exponentialGoalAvWeighted(goalsArray):
  exponential = [math.exp(-i/5) for i in range(len(goalsArray))]
  return np.average(np.array(goalsArray),weights=exponential)

def teamLookBackGoals(lookupTable,lookbackDays):
  Table = []
  lookBack = reconstructGameLog(lookbackDays)
  #try to lookBack this
  for i in lookupTable.ID.values:
    try:
      arrays = teamReconstruction(i,lookBack)
      avGoals = exponentialGoalAvWeighted(arrays)
      Table += [[i,avGoals,arrays]]
    except:
      continue
  Today = pd.DataFrame(Table)
  Today.columns = ['ID','avGoals','Goal LookBack']
  return Today

#Visualizations per game if desired
def visualizeMatrix(Matrix):
  Home = [i for i in range(8)]*8#change this to discrete step
  Away=[]
  for i in range(8):
    Away += [i]*8
  probability = Matrix.ravel()
  source = pd.DataFrame({'HomeGoals':Home, 'AwayGoals':Away,'Probability':probability})
  base = alt.Chart(source).mark_rect().encode(
    x='HomeGoals:O',
    y=alt.Y('AwayGoals:O',
        sort=alt.EncodingSortField('AwayGoals', order='descending')),
    color='Probability:Q'
  ).configure_scale(
    bandPaddingInner=0.1
  ).properties(
    width=400,
    height=400
  )
  
  return base

def visualizeExpectations(Matrix,Payouts):
  Home = [i for i in range(8)]*8 #change this to discrete step
  Away=[]
  for i in range(8):
    Away += [i]*8
  probability = Matrix.ravel()
  source = pd.DataFrame({'HomeGoals':Home, 'AwayGoals':Away,'Probability':probability})
  return alt.Chart(source).mark_rect().encode(
    x='HomeGoals:O',
    y=alt.Y('AwayGoals:O',
        sort=alt.EncodingSortField('AwayGoals', order='descending')),
    color='Probability:Q'
  ).configure_scale(
    bandPaddingInner=0.1
  ).properties(
    width=400,
    height=400
  )
  
#odds to game transformation
def identify(i,teamID= teamID):
  if i!= 'Tie':
    return teamID[teamID.Name == i].Abbr.values[0]
  else:
    return 'Tie'

def betFunction(game, betName,parameterArray, GoalsLookup):
  #this is basically a massive switch case
  if betName == '60 Minute Line':
    gameName, Team, oddsDec = game, parameterArray[0], parameterArray[1]
    return [gameName, identify(Team), oddsDec, '60E']
  elif betName == 'Money Line':
    gameName, Team, oddsDec = game, parameterArray[0], parameterArray[1]
    return [gameName, identify(Team), oddsDec, 'ML']
  elif betName == 'Both Teams to Score':
    gameName, Result, oddsDec = game, parameterArray[0], parameterArray[1]
    #print('BTTS param array', parameterArray[0], parameterArray[1])
    return [gameName, Result, oddsDec, 'BTTS']
  else:
    return [np.NaN, np.NaN, np.NaN, np.NaN]

def getavGoals(GoalsLookup, TeamName):
	if TeamName != 'Tie':
		return (GoalsLookup[GoalsLookup.Abbr == TeamName][['avGoals']].values[0])[0]
	else: 
		return None

def winner60(matrix, homeaway):
  if homeaway == "home":
    return np.sum(np.triu(matrix,1))
  elif homeaway == "away":
    return np.sum(np.tril(matrix,-1))
  else:
    return np.sum(np.diagonal(matrix))

def betDecisionAfter60(avGoalsHome,avGoalsAway,odds,bet):
  matrix = poissonMatrix(avGoalsHome,avGoalsAway)
  payouts = [bet+i for i in odds] #look on fanduel you will see it needs to be additive not multiplicative - this is somewhere in the odds pulling but its not an issue
  probs = [winner60(matrix,i) for i in ['home','tie','away']]
  kelly = [Kelly(payouts[i],probs[i]) for i in range(len(probs))]
  decisions = [payouts[i]*probs[i] for i in range(len(payouts))]
  placed = []
  for i in decisions:
  	if i>1.0:
  		placed += [decisions.index(i),kelly[decisions.index(i)],(probs[decisions.index(i)]-1/payouts[decisions.index(i)]),payouts[decisions.index(i)]]
  	else:
  		continue
  return placed

def winnerOneOT(matrix,homeoraway,avGoalsHome,avGoalsAway):
  if homeoraway == 'home':
    reg = np.sum(np.triu(matrix,1).ravel())
    win = reg + (np.sum(np.diagonal(matrix)))*(avGoalsHome/(avGoalsHome+avGoalsAway)) # do lambda/lambda+lambda
    return win
  if homeoraway == 'away':
    reg = np.sum(np.tril(matrix,-1).ravel())
    win = reg + (np.sum(np.diagonal(matrix)))*(avGoalsAway/(avGoalsHome+avGoalsAway))
    return win

def betDecisionMoneylineOT(avGoalsHome,avGoalsAway,odds,bet):
  matrix = poissonMatrix(avGoalsHome,avGoalsAway)
  payouts = [bet+i for i in odds] #look on fanduel you will see it needs to be additive not multiplicative - this is somewhere in the odds pulling but its not an issue
  probs = [winnerOneOT(matrix,i,avGoalsHome,avGoalsAway) for i in ['home','away']]
  kelly = [Kelly(payouts[i],probs[i]) for i in range(len(probs))]
  decisions = [payouts[i]*probs[i] for i in range(len(payouts))]
  #print(probs, payouts, decisions)
  placed = []
  for i in decisions:
  	if i>1.0:
  		placed += [decisions.index(i),kelly[decisions.index(i)],(probs[decisions.index(i)]-1/payouts[decisions.index(i)]),payouts[decisions.index(i)]]
  	else:
  		continue
  return placed
  
def bothScore(matrix,homeoraway,avGoalsHome,avGoalsAway):
  if homeoraway == 'Yes':
  	reg = 1 - (np.sum(matrix[0,1:]) + np.sum(matrix[1:,0]) + matrix[0,0])
  	return reg
  if homeoraway == 'No':
    reg = (np.sum(matrix[0,1:]) + np.sum(matrix[1:,0]) + matrix[0,0])
    return reg 
     
def betDecisionBothScore(avGoalsHome,avGoalsAway,odds,bet):
  matrix = poissonMatrix(avGoalsHome,avGoalsAway)
  payouts = [bet+i for i in odds] #look on fanduel you will see it needs to be additive not multiplicative - this is somewhere in the odds pulling but its not an issue
  probs = [bothScore(matrix,i,avGoalsHome,avGoalsAway) for i in ['Yes','No']]
  kelly = [Kelly(payouts[i],probs[i]) for i in range(len(probs))]
  decisions = [payouts[i]*probs[i] for i in range(len(payouts))]
  #print(probs, payouts, decisions)
  placed = []
  for i in decisions:
  	if i>1.0:
  		placed += [[decisions.index(i),kelly[decisions.index(i)],(probs[decisions.index(i)]-1/payouts[decisions.index(i)]),payouts[decisions.index(i)]]]
  	else:
  		continue
  #print(placed) you need to figure out hwo to show both
  return placed

def betSwitchImplement(types, df):
	if types == '60E':
		try:	
			yields = betDecisionAfter60(df.Goals.values[0],df.Goals.values[2],df.Odds.values,bet=1)
			return [types, df.Teams.values[yields[0]], yields[1],yields[2],yields[3]]
		except:
			#print(yields)
			return [types,np.NaN,np.NaN,np.NaN,]
	elif types =='ML':
		try:
			yields = betDecisionMoneylineOT(df.Goals.values[0],df.Goals.values[1],df.Odds.values,bet=1)
			return [types, df.Teams.values[yields[0]], yields[1],yields[2],yields[3]]
		except:
			return [types, np.NaN,np.NaN,np.NaN,np.NaN]
	elif types =='BTTS':
		try:
			yields = betDecisionBothScore(df.Goals.values[0],df.Goals.values[1],df.Odds.values,bet=1)
			return [types, df.Result.values[yields[0]], yields[1],yields[2],yields[3]]
		except:
			return [types, np.NaN,np.NaN,np.NaN,np.NaN]

def identifyName(temp,toggle):
	if toggle == 'away':
		return temp.Game.values[0].split('At')[0][0:-1]
	elif toggle == 'home':
		return temp.Game.values[0].split('At')[1][1:]

def placeBet(temp, GoalsLookup):
	if temp.Type.values[0] =='BTTS':
		types = temp.Type.values[0]
		Result = temp.Team.values
		Odds = temp.DecimalOdds.values
		Teams = [identifyName(temp,'away'), identifyName(temp,'home')]
		avGoals = [getavGoals(GoalsLookup, identify(i)) for i in Teams]
		goalDf = pd.DataFrame({'Result':Result, 'Goals':avGoals, 'Odds':Odds})
		bets = betSwitchImplement(types, goalDf)
		return bets
		
	else:
		types = temp.Type.values[0]
		Teams = temp.Team.values
		Odds = temp.DecimalOdds.values
		avGoals = [getavGoals(GoalsLookup, i) for i in Teams]
		goalDf = pd.DataFrame({'Teams':Teams, 'Goals':avGoals, 'Odds':Odds})
		bets = betSwitchImplement(types, goalDf)
		return bets

def dailyBetParse(oddsDataFrame,LU):
	try:
		placedBet = []
		for i in np.unique(oddsDataFrame.Type.values):
			temp = oddsDataFrame[oddsDataFrame.Type == i]
			placedBet += [placeBet(temp,LU)]
			#print(placedBet)
		BetFrame = pd.DataFrame(placedBet)
		BetFrame = BetFrame.dropna()
		BetFrame.columns = ['Bet Type','Bet State Chosen', 'Kelly Criterion Suggestion', 'Probability Spread','Payouts (per Dollar)']
		return BetFrame
	except:
		return 'No Bets Worthwhile Today'
		
def gameToday():
	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/56572.3.json').json()
	boolean = searchingForGame(jsonData_fanduel_epl)
	return boolean
	
def searchingForGame(jsonData):
	results_df = pd.DataFrame()
	alpha = jsonData['events'][0]
	gameday = alpha['tsstart'][:10]
	today = str(date.today())
	#print(today, gameday)
	return today == gameday

def powerLaw(portfolioAmt,df):
  probs = np.array([(1-(1/i)) for i in df['Payouts (per Dollar)'].values]) #can be used for higher risk tolerance though unused here
  amount = 1/np.prod(probs) #test portfolio constraints
  kelly = df['Kelly Criterion Suggestion'].values
  spread = df['Probability Spread'].values
  allocation1 = [np.minimum((portfolioAmt*i)*(i/np.sum(kelly)), 0.3*portfolioAmt) for i in kelly] #RISK TOLERANCE ESTABLISHED HERE 
  df['Allocation Dollars'] = allocation1
  print('Total Allocated', np.sum(allocation1), 'out of', portfolioAmt)
  df['Allocation Percentage'] = [(i/portfolioAmt) for i in allocation1]
  return df

def gainsLosses(allocation,successes, df, portfolio):
  payouts = df['Payouts (per Dollar)'].values
  prev = np.sum(allocation)
  now = np.sum(np.dot([allocation[i]*payouts[i] for i in range(len(payouts))], successes))
  return [portfolio+(now-prev), prev, now]

def picks(): #this needs some work/checking
	result = fetch().round(decimals=2)
	resulting = result[['Bet State Chosen', 'Kelly Criterion Suggestion','Payouts (per Dollar)']]
	resulting['League'] = ['NHL']*len(resulting['Bet State Chosen'])
	resulting['Date'] = [str(date.today())]*len(resulting['Bet State Chosen'])
	resulting.to_csv(os.getcwd() + '/masterDaily.csv', mode='a', header=False)
	return 'NHL Done'
	
#_____________________________________IMPLEMENTATION_______________________________________________


def picks(teamID = teamID):
	print('Just wait a moment while we retreive todays teams, odds, and historical data.')
	GoalsLookup = pd.merge(teamID, teamLookBackGoals(teamID,21),on='ID')
	print(GoalsLookup)
	oddsDataFrame = fetch(GoalsLookup)
	Daily = dailyBetParse(oddsDataFrame,GoalsLookup)
	print(Daily)
	result = Daily.round(decimals=2)
	results = result[result['Bet Type'] == 'ML']
	print(results.to_markdown())
	resulting = results[['Bet State Chosen', 'Kelly Criterion Suggestion','Payouts (per Dollar)']]
	resulting['League'] = ['NHL']*len(resulting['Bet State Chosen'])
	resulting['Date'] = [str(date.today())]*len(resulting['Bet State Chosen'])
	resulting.to_csv(os.getcwd() + '/masterDaily.csv', mode='a', header=False)
	return 'NHL Done'

def run():
	if gameToday():
		return picks()
	else:
		return ('No NHL games today.')

print(run())

#make an odds tracker, how to identify the peak?


