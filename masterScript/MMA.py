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
import warnings
import re

warnings.filterwarnings("ignore") 

def matching(arrayStrOne,arrayStrTwo):
	matches = []
	for i in arrayStrOne:
		attempt = [fuzz.token_sort_ratio(str(i), str(j)) for j in arrayStrTwo]
		#print(attempt)
		matches += [arrayStrTwo[np.argmax(attempt)]]
	return attempt

def tryMatch(i,j):
	return fuzz.token_sort_ratio(str(i), str(j))
	
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
    print(jsonData)
    for alpha in jsonData['events']:
        gameday = (alpha['tsstart'][:10])
        if (gameday == str(date.today()+ timedelta(2))):
        	print ('Gathering %s data: %s @ %s' %(alpha['sportname'],alpha['participantname_away'],alpha['participantname_home']))
        	alpha_df = json_normalize(alpha).drop('markets',axis=1)
        	for beta in alpha['markets']:
        		#print(beta['selections']) #merge "getOdds" with this parse
        		beta_df = json_normalize(beta).drop('selections',axis=1)
        		beta_df.columns = [str(col) + '.markets' for col in beta_df.columns]
        		print(beta_df)
        		for theta in beta['selections']:
        			theta_df = json_normalize(theta)
        			theta_df.columns = [str(col) + '.selections' for col in theta_df.columns]
        		
        			temp_df = reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True), [alpha_df, beta_df, theta_df])
        			results_df = results_df.append(temp_df, sort=True).reset_index(drop=True)
    return results_df #time right for <7 on prev day

def fullSet(eventID):
  return requests.get('https://sportsbook.fanduel.com//cache/psevent/UK/1/false/'+ str(eventID) + '.json').json()

def searchingForGame(jsonData):
	results_df = pd.DataFrame()
	alpha = jsonData['events'][0]
	gameday = alpha['tsstart'][:10]
	today = str(date.today())
	print(today, gameday)
	return today == gameday

def gameToday():
	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/50361.3.json').json()
	boolean = searchingForGame(jsonData_fanduel_epl)
	return boolean

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
  #print(len(listing), "HELLO")
  for game in listing:
  	for i in game['eventmarketgroups'][0]['markets']:
  		#print(i['name'])
  		betName = [game['externaldescription'], i['name']]
  		if i['name'] == 'Moneyline':
  			for i in i['selections']:
  				#print([i['name'], 1+(i['currentpriceup']/i['currentpricedown'])])
  				betName+=[[i['name'], 1+(i['currentpriceup']/i['currentpricedown'])]] #, i['currenthandicap']
  		bets += [betName]
  return bets

def fetch():
  try:
  	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/50361.3.json').json() #gives the game id
  except:
  	print('Not a problem, the XHR has been changed for MMA, go ahead and fix that then run again')
  epl = parse_data(jsonData_fanduel_epl)
  EPL = pd.DataFrame(epl)[['eventname','tsstart','idfoevent.markets']]
  EPL.columns = ['Teams','Date','EventID']
  listing = []
  for i in np.unique(EPL.EventID.values): 
    listing.append((fullSet(i)))
  df = (pd.DataFrame(getOdds(listing)))
  print(df)
  df.columns = ['GameName', 'Type', 'HomeTeamandOdds', 'AwayTeamandOdds']
  df = df[df.Type=='Moneyline']
  probabilities = fetchName()
  
  #check if all of them are there
  valued = []
  print(probabilities.gameNum.values)
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
  	print(temp)
  	sought = (sorting[temp.index(np.max(temp))])
  	soughtgameNum = probabilities[probabilities.ID == sought].gameNum.values[0]
  	counterArray += [counter]
  	soughtGameArray += [soughtgameNum]
  	counter += 1
  	
  fixed = pd.DataFrame({'sought':soughtGameArray, 'linked':counterArray}).sort_values(['sought'])
  print(fixed)
  linker = []
  
  for i in fixed.linked.values:
  	linker += [i]
  	linker += [i]
  print(len(probabilities['gameNum']), len(linker))
  probabilities['gameNum'] = linker
  print(probabilities)
  
  array ,counter = [], 0
  for i in probabilities.gameNum.values:
  	print(counter)
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
  
def lookBackAnalysis():
  url = 'https://www.mmabot.com/upcoming-events'
  
  #print('hello')
  page_response = requests.get(url, timeout=10, headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'Cookies':'fbp=fb.1.1614007657803.38313793; _ga=GA1.2.1857830574.1614007658; _gid=GA1.2.234349248.1614007658; ac_enable_tracking=1; outbrain_cid_fetch=true; 12c5c06416db37186f39465beb5f7b67=c02040eadf89229fbe127d99379615f2; joomla_remember_me_bf2da9a3a077b14a5925756bbb5146ad=ZnAajc7TxrKwvxTP.O4B8LhCwKHs6M6KKIYhU; joomla_user_state=logged_in',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
  page_content = BeautifulSoup(page_response.content, "html.parser")
  navigate = page_content.findAll('div', class_="events-cat-event")
  print(navigate)
  teamsToday, probabilitiesToday, Odds,date,winners = [],[], [],[],[]
  for j in navigate:
  	extension = str(j).split("=")[2][1:-14]
  	print(extension)
  	urlExtension = str('https://www.mmabot.com' + extension)
  	page_response_extended = requests.get(urlExtension, timeout=5, headers = { 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',    'accept-encoding': 'gzip, deflate, br','accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3','cache-control': 'max-age=0','upgrade-insecure-requests': '1','Cookies':'fbp=fb.1.1614007657803.38313793; _ga=GA1.2.1857830574.1614007658; _gid=GA1.2.234349248.1614007658; ac_enable_tracking=1; outbrain_cid_fetch=true; 12c5c06416db37186f39465beb5f7b67=c02040eadf89229fbe127d99379615f2; joomla_remember_me_bf2da9a3a077b14a5925756bbb5146ad=ZnAajc7TxrKwvxTP.O4B8LhCwKHs6M6KKIYhU; joomla_user_state=logged_in', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
  	fight_contents = BeautifulSoup(page_response_extended.content, "html.parser")
  	try:
  		for i in fight_contents.findAll('div', class_ = 'fight'):
  			names = [k.find('strong').text for k in i.findAll('div', class_ = 'hasLink')]
  			odds = [k.find('div').text for k in i.findAll('div', class_ = 'hasLink')]
  			Date = '-'.join(extension.split('-')[-3:])
  			winner = [k.text for k in i.findAll('div', class_ = 'fighter-label')]
  			if len(i.findAll('div', class_ = "prediction-bar-prob fighter1"))==0:
  				probFighter1 = float(i.findAll('div', class_ = "prediction-bar-prob fighter1 picked")[0].text.strip()[:-1])/100
  				probFighter2 = float(i.findAll('div', class_ = "prediction-bar-prob fighter2")[0].text.strip()[:-1])/100
  				name1 = names[0]
  				name2 = names[1]
  				odds1 = odds[0].split(' ')[0][-4:]
  				odds2 = odds[1].split(' ')[0][-4:]
  				winner1 = winner[0]
  				winner2 = winner[1]
  				
  	
  			else:
  				probFighter1 = float(i.findAll('div', class_ = "prediction-bar-prob fighter1")[0].text.strip()[:-1])/100
  				probFighter2 = float(i.findAll('div', class_ = "prediction-bar-prob fighter2 picked")[0].text.strip()[:-1])/100
  				name1 = names[0]
  				name2 = names[1]
  				odds1 = odds[0].split(' ')[0][-4:]
  				odds2 = odds[1].split(' ')[0][-4:]
  				winner1 = winner[0]
  				winner2 = winner[1]
  				
  		  
  			teamsToday += [name1, name2]
  			probabilitiesToday += [probFighter1, probFighter2]
  			Odds += [odds1, odds2]
  			date += [Date, Date]
  			winners += [winner1,winner2]
  			
  	except:
  		continue
  		
  indexed = []
  for i in range(int(len(teamsToday)/2)):
    indexed += [i]*2
  
  mma = pd.DataFrame({'ID':teamsToday, 'Probabilities':probabilitiesToday, 'Odds':Odds, 'Date':date , 'gameNum': indexed, 'Winner':winners})
  print(mma)
  mma.to_csv('./mmaLookbackValueSystem.csv')
  return 'Done'	
	
	
	
	
	
	
def fetchName(): 
  url = 'https://www.mmabot.com/upcoming-events'
  
  #print('hello')
  page_response = requests.get(url, timeout=10, headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'Cookies':'fbp=fb.1.1614007657803.38313793; _ga=GA1.2.1857830574.1614007658; _gid=GA1.2.234349248.1614007658; ac_enable_tracking=1; outbrain_cid_fetch=true; 12c5c06416db37186f39465beb5f7b67=c02040eadf89229fbe127d99379615f2; joomla_remember_me_bf2da9a3a077b14a5925756bbb5146ad=ZnAajc7TxrKwvxTP.O4B8LhCwKHs6M6KKIYhU; joomla_user_state=logged_in',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
  page_content = BeautifulSoup(page_response.content, "html.parser")
  navigate = page_content.findAll('div', class_="events-cat-event")
  extension = str(navigate).split("=")[2][1:-14]
  print(len(navigate))
  urlExtension = str('https://www.mmabot.com' + extension)
  print(urlExtension)
  page_response_extended = requests.get(urlExtension, timeout=5, headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'Cookies':'fbp=fb.1.1614007657803.38313793; _ga=GA1.2.1857830574.1614007658; _gid=GA1.2.234349248.1614007658; ac_enable_tracking=1; outbrain_cid_fetch=true; 12c5c06416db37186f39465beb5f7b67=c02040eadf89229fbe127d99379615f2; joomla_remember_me_bf2da9a3a077b14a5925756bbb5146ad=ZnAajc7TxrKwvxTP.O4B8LhCwKHs6M6KKIYhU; joomla_user_state=logged_in',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
  fight_contents = BeautifulSoup(page_response_extended.content, "html.parser")

  teamsToday, probabilitiesToday = [],[]
  for i in fight_contents.findAll('div', class_ = 'fight'):
  	names = [j.find('strong').text for j in i.findAll('div', class_ = 'hasLink')]
  	if len(i.findAll('div', class_ = "prediction-bar-prob fighter1"))==0:
  		probFighter1 = float(i.findAll('div', class_ = "prediction-bar-prob fighter1 picked")[0].text.strip()[:-1])/100
  		probFighter2 = float(i.findAll('div', class_ = "prediction-bar-prob fighter2")[0].text.strip()[:-1])/100
  		name1 = names[0]
  		name2 = names[1]
  	
  	else:
  		probFighter1 = float(i.findAll('div', class_ = "prediction-bar-prob fighter1")[0].text.strip()[:-1])/100
  		probFighter2 = float(i.findAll('div', class_ = "prediction-bar-prob fighter2 picked")[0].text.strip()[:-1])/100
  		name1 = names[0]
  		name2 = names[1]
  		  
  	teamsToday += [name1, name2]
  	probabilitiesToday += [probFighter1, probFighter2]
  indexed = []
  for i in range(int(len(teamsToday)/2)):
  	indexed += [i]*2
  mma = pd.DataFrame({'ID':teamsToday, 'Probabilities':probabilitiesToday, 'gameNum':indexed })
  print(mma)
  return mma

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

def picks(): #this needs some work/checking
	result = fetch().round(decimals=2)
	print(result.to_markdown())
	resulting = result[['Bet State Chosen', 'Kelly Criterion Suggestion','Payouts (per Dollar)']]
	resulting['League'] = ['MMA']*len(resulting['Bet State Chosen'])
	resulting['Date'] = [str(date.today())]*len(resulting['Bet State Chosen'])
	#resulting.to_csv(os.getcwd() + '/masterDaily.csv', mode='a', header=False)
	return 'MMA Done'
	
'''
To do:
-- comment some more stuff and figure out hwo to implement NHl in this exact framework, maybe jsut replace the XHR, but the bettting is different, run seperately?
-- add over under, period bets, make the names for tie more clear if possible
-- make tree structure easy to implement

Notes:
-- works 00:00 day of'''
#Make a time function


def run():
	if gameToday():
		return None #picks()
	else:
		return 'No MMA fights today.'

print(run())
print(lookBackAnalysis())
	
