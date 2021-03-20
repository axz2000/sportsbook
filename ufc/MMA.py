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
	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/50361.3.json').json()
	boolean = searchingForGame(jsonData_fanduel_epl)
	return boolean

def fetch():
  try:
  	jsonData_fanduel_nba = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/50361.3.json').json() #gives the game id
  except:
  	print('Not a problem, the XHR has been changed for the NBA, go ahead and fix that then run again')
  epl = parse_data(jsonData_fanduel_nba)
  print(epl)
  EPL = pd.DataFrame(epl)[['eventname','tsstart','idfoevent.markets']]
  EPL.columns = ['Teams','Date','EventID']
  listing = []
  for i in np.unique(EPL.EventID.values): 
    listing.append((fullSet(i)))
  df = (pd.DataFrame(getOdds(listing)))
  df.columns = ['GameName', 'Type', 'HomeTeamandOdds', 'AwayTeamandOdds']
  df = df[df.Type=='Moneyline']
  #print(df.sort_values(['GameName']))
  probabilities = fetchName()
  fighter, odds = [], []
  for i in df.GameName:
  	dfnew = df[df.GameName == i]
  	fighter += [dfnew.HomeTeamandOdds.values[0][0],dfnew.AwayTeamandOdds.values[0][0]]
  	odds += [dfnew.HomeTeamandOdds.values[0][1],dfnew.AwayTeamandOdds.values[0][1]]
  	#array += [[dfnew.HomeTeamandOdds.values[0][0],dfnew.HomeTeamandOdds.values[0][1]],[dfnew.AwayTeamandOdds.values[0][0],dfnew.AwayTeamandOdds.values[0][1]]]
  newest = pd.DataFrame({'ID':fighter,'Odds':odds})
  Result = (probabilities.set_index('ID').join(newest.set_index('ID'))).reset_index()
  Result['EV'] = [Result.Probabilities.values[i] * Result.Odds.values[i] for i in range(len(Result))]
  Result['Team'] = Result.ID.values
  Result['Probability'] = Result.Probabilities.values
  Result = Result[['Team','Probability','Odds','EV']]
  Bet = Result[Result.EV >1.07]
  kelly = [Kelly(Bet.Odds.values[i], Bet.Probability.values[i]) for i in range(len(Bet.Probability.values))]
  #print(len(Bet.Team.values), len(kelly),  len(Bet.Odds.values))
  Betting = pd.DataFrame({'Bet State Chosen':Bet.Team.values, 'Kelly Criterion Suggestion': kelly, 'Payouts (per Dollar)':Bet.Odds.values})
  #Betting.columns = ['Bet State Chosen', 'Kelly Criterion Suggestion', 'Probability Spread','Payouts (per Dollar)']
  return Betting
  
	
def fetchName(): 
  url = 'https://www.mmabot.com/upcoming-events'
  
  #print('hello')
  page_response = requests.get(url, timeout=10, headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'Cookie':'_fbp=fb.1.1616256099852.1318259178; _ga=GA1.2.1675793287.1616256099; _gid=GA1.2.498386498.1616256099; ac_enable_tracking=1; 12c5c06416db37186f39465beb5f7b67=3674853899c2340e90ea0f643cebe74a; joomla_remember_me_bf2da9a3a077b14a5925756bbb5146ad=l2zRj4slJ6iill8K.W6wiN9cqQEFJZ40SiDeF; joomla_user_state=logged_in; outbrain_cid_fetch=true',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
  page_content = BeautifulSoup(page_response.content, "html.parser")
  navigate = page_content.findAll('div', class_="events-cat-event")
  extension = str(navigate).split("=")[2][1:-14]
  urlExtension = str('https://www.mmabot.com' + extension)
  print(urlExtension)
  fight_contents = requests.get(urlExtension, timeout=10, headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'Cookie':'_fbp=fb.1.1616256099852.1318259178; _ga=GA1.2.1675793287.1616256099; _gid=GA1.2.498386498.1616256099; ac_enable_tracking=1; 12c5c06416db37186f39465beb5f7b67=3674853899c2340e90ea0f643cebe74a; joomla_remember_me_bf2da9a3a077b14a5925756bbb5146ad=l2zRj4slJ6iill8K.W6wiN9cqQEFJZ40SiDeF; joomla_user_state=logged_in; outbrain_cid_fetch=true',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
  fight_contents = BeautifulSoup(fight_contents.content, "html.parser")
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
  mma = mma[mma.ID != 'William Knight']
  mma = mma[mma.ID != 'Alonzo Menifield']
  mma = mma[mma.ID != 'Alex Oliveira']
  mma = mma[mma.ID != 'Ramazan Kuramagomedov']
  indexer = []
  for i in range(int(len(mma.ID)/2)):
  	indexer += [i]*2
  mma['gameNum'] = indexer
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

def picks():
	result = fetch().round(decimals=2)
	print(result.to_markdown())
	resulting = result[['Bet State Chosen', 'Kelly Criterion Suggestion','Payouts (per Dollar)']]
	resulting['League'] = ['MMA']*len(resulting['Bet State Chosen'])
	resulting['Date'] = [str(date.today())]*len(resulting['Bet State Chosen'])
	resulting.to_csv(os.getcwd() + '/masterDaily.csv', mode='a', header=False)
	return 'MMA Done'


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
		return ('No MMA games today.')

print(run())
def tryScrape():

	with requests.Session() as s:
		p = s.post("https://mmabot.com", data={"email": 'brilliantscarcity354@gmail.com', "password": "BrilliantScarcity354"})
		print(p.text)
		base_page = s.get('https://www.mmabot.com')
		soup = BeautifulSoup(base_page.content, 'html.parser')
		return soup