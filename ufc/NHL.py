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
def fullSet(eventID):
  return requests.get('https://sportsbook.fanduel.com//cache/psevent/UK/1/false/'+ str(eventID) + '.json').json()

def searchingForGame(jsonData):
	results_df = pd.DataFrame()
	alpha = jsonData['events'][0]
	gameday = alpha['tsstart'][:10]
	today = str(date.today())
	#print(today, gameday)
	return today == gameday
  
def gameToday():
	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/49694.3.json').json()
	boolean = searchingForGame(jsonData_fanduel_epl)
	return boolean

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
  		if i['name'] == 'Money Line':
  			for i in i['selections']:
  				betName+=[[i['name'], 1+(i['currentpriceup']/i['currentpricedown'])]] #, i['currenthandicap']
  		bets += [betName]
  return bets

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

def fetch():
  try:
  	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/56572.3.json').json() #gives the game id
  except:
  	print('Not a problem, the XHR has been changed for the EPL, go ahead and fix that then run again')
  epl = parse_data(jsonData_fanduel_epl)
  print(epl)
  EPL = pd.DataFrame(epl)[['eventname','tsstart','idfoevent.markets']]
  EPL.columns = ['Teams','Date','EventID']
  listing = []
  for i in np.unique(EPL.EventID.values): 
    listing.append((fullSet(i)))
  df = (pd.DataFrame(getOdds(listing)))
  print(df)
  df.columns = ['GameName', 'Type', 'HomeTeamandOdds', 'AwayTeamandOdds']
  df = df[df.Type=='Money Line']
  #df = df[df.GameName != 'Shrewsbury v Lincoln']
  probabilities = fetchName()
  print(probabilities)
  
  #check if all of them are there
  valued = []
  #print(probabilities.gameNum.values)
  for i in np.unique(probabilities.gameNum.values):
  	newdf = probabilities[probabilities.gameNum == i]
  	valued += [newdf.ID.values[1][:]]
  	print(valued)
  sorting = np.sort(valued)
  indices, counterArray, soughtGameArray = [], [], []
  counter = 0
  gamed = []
  
  #print((len(df.GameName.values), len(sorting)))
  for i in (df.GameName.values):
  	temp = []
  	for j in np.unique(sorting):
  		temp += [tryMatch(i,j)]
  	#print(temp)
  	sought = (sorting[temp.index(np.max(temp))])
  	soughtgameNum = probabilities[probabilities.ID == sought].gameNum.values[0]
  	counterArray += [counter]
  	soughtGameArray += [soughtgameNum]
  	counter += 1
  	
  fixed = pd.DataFrame({'sought':soughtGameArray, 'linked':counterArray}).sort_values(['sought'])
  #print(fixed)
  linker = []
  
  for i in fixed.linked.values:
  	linker += [i]
  	linker += [i]
  #print(len(probabilities['gameNum']), len(linker))
  probabilities['gameNum'] = linker
  #print(probabilities)
  
  array ,counter = [], 0
  for i in probabilities.gameNum.values:
  	#print(counter)
  	if counter%2 == 0:
  		indexed = probabilities.gameNum.values[counter]
  		#print(df.HomeTeamandOdds.values[indexed][-1])
  		valued = df.HomeTeamandOdds.values[i][-1]
  		array+= [valued]
  		counter = counter+1
  	else:
  		indexed = probabilities.gameNum.values[counter]
  		valued = df.AwayTeamandOdds.values[i][-1]
  		array += [valued]
  		counter = counter+1
  EV = []
  for i in range(len(array)):
  	EV += [probabilities.Probabilities.values[i]*array[i]]
  #print(array, probabilities.ID.values,probabilities )
  Result = pd.DataFrame({'Team':probabilities.ID.values, 'Probability': probabilities.Probabilities.values, 'Odds':array, 'EV':EV})
  print(Result)
  Bet = Result[Result.EV >1]
  kelly = [Kelly(Bet.Odds.values[i], Bet.Probability.values[i]) for i in range(len(Bet.Probability.values))]
  #print(len(Bet.Team.values), len(kelly),  len(Bet.Odds.values))
  Betting = pd.DataFrame({'Bet State Chosen':Bet.Team.values, 'Kelly Criterion Suggestion': kelly, 'Payouts (per Dollar)':Bet.Odds.values})
  #Betting.columns = ['Bet State Chosen', 'Kelly Criterion Suggestion', 'Probability Spread','Payouts (per Dollar)']
  return Betting

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

def betSwitchImplement(types, dfbig):
	if types == '60E':
		yayray = []
		for i in range(int(len(dfbig.Teams.values)/3)):
			df = dfbig[int(i*3):int(i*3+3)]
			#print(betDecisionAfter60(df.Goals.values[0],df.Goals.values[2],df.Odds.values,bet=1))
			try:
				#print(betDecisionAfter60(df.Goals.values[0],df.Goals.values[2],df.Odds.values,bet=1))	
				yields = betDecisionAfter60(df.Goals.values[0],df.Goals.values[2],df.Odds.values,bet=1)
				yayray.append([types, df.Teams.values[yields[0]], yields[1],yields[2],yields[3]])
			except:
				#print(yields)
				yayray.append([types,np.NaN,np.NaN,np.NaN,np.NaN])
		#print(yayray)
		return yayray
		
	elif types =='ML':
		yayray = []
		for i in range(int(len(dfbig.Teams.values)/2)):
			df = dfbig[int(i*2):int(i*2+2)]
			try:
				yields = betDecisionMoneylineOT(df.Goals.values[0],df.Goals.values[1],df.Odds.values,bet=1)
				yayray.append([types, df.Teams.values[yields[0]], yields[1],yields[2],yields[3]])
			except:
				#print(yields)
				yayray.append([types,np.NaN,np.NaN,np.NaN,np.NaN])
		#print(yayray)
		return yayray
	elif types =='BTTS':
		try:
			yields = betDecisionBothScore(df.Goals.values[0],df.Goals.values[1],df.Odds.values,bet=1)
			return [types, df.Result.values[yields[0]], yields[1],yields[2],yields[3]]
		except:
			return [types, np.NaN,np.NaN,np.NaN,np.NaN]
			
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


def placeBet(temp, GoalsLookup):
		types = temp.Type.values[0]
		Teams = temp.Team.values
		Odds = temp.DecimalOdds.values
		avGoals = [getavGoals(GoalsLookup, i) for i in Teams]
		goalDf = pd.DataFrame({'Teams':Teams, 'Goals':avGoals, 'Odds':Odds})
		bets = betSwitchImplement(types, goalDf)
		print(bets)
		return bets

def dailyBetParse(oddsDataFrame,GoalsLookup):
	placedBet = []
	for i in np.unique(oddsDataFrame.Type.values):
		temp = oddsDataFrame[oddsDataFrame.Type == i]
		here = placeBet(temp,GoalsLookup)
		for i in here:
			placedBet += [i]
	BetFrame = pd.DataFrame(placedBet)
	BetFrame = BetFrame.dropna()
	BetFrame.columns = ['Bet Type','Bet State Chosen', 'Kelly Criterion Suggestion', 'Probability Spread','Payouts (per Dollar)']
	return BetFrame
		
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

print(fetch())

#make an odds tracker, how to identify the peak?


