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
from matplotlib import pyplot as plt 
import simultaneousKelly
pd.options.mode.chained_assignment = None  # default='warn'
	    
def checkingKelly(typing, start = 153):
	df = pd.read_csv('~/Desktop/sportsbook/masterScript/historicalBetLedger.csv')
	#df = df.loc[int(len(df)/2):]
	df["Allocation Percentage"] = df["Allocation Percentage"].astype('float64') 
	net = 0
	portfolio = start
	array = [153]
	counter = 0
	for i in np.unique(df.Date.values):
		new = df[df.Date == i]
		if len(new)>8:
			new = new.sort_values(['Kelly Criterion Suggestion'], ascending = False)[:8]
			#print(new)
		else:
			new = new
		ar, bp = new['Kelly Criterion Suggestion'].values, new['Payouts (per Dollar)'].values
		#print(ar,bp)
		try:
			print(i)
			yeswedid = simultaneousKelly.run(bp,ar)*array[-1]*(5/8)
			#print(yeswedid)
			portnew = np.sum(yeswedid*new['Success'].values* new['Payouts (per Dollar)'].values)
			net = portnew - sum(yeswedid)
			portfolio += net
			array.append(portfolio)
			print(portfolio)
			if (len(array)%10 == 0):
				print(len(array)/len(df))
		except:
			print(i)
			continue
	if typing == 'array':
		return array
	else:
		return portfolio

def simKelly():
	sims = checkingKelly('array')
	plt.plot(np.arange(len(sims)),sims)
	plt.yscale('log')
	plt.show()
	return None

def ye():
  url = "https://nf-api.numberfire.com/v0/drives?apikey=37cb736b06d64ca6ae8f3ca2c0797582&sport=nba&game_id=26277.json"
  #print('hello')
  '''page_response = requests.get(url, timeout=10, headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
  page_content = BeautifulSoup(page_response.content, "html.parser")'''
  ordering = (requests.get(url).json())[0]['play_order']
  listing = (requests.get(url).json())[0]['plays']
  yay = []
  for i in ordering:
  	print(i)
  	yay.append(listing[str(i)]['home_wp'])
  return (yay, 'these are the win probabilities mid game')
  
def run():
	listing = gs.search(('Python'))
	print(listing)
	return 'Done'
	
def geo_mean_overflow(iterable):
    a = np.log(iterable)
    return np.exp(a.mean())
    
def check(j,typing, start = 153):
	df = nba()
	df["Allocation Percentage"] = df["Allocation Percentage"].astype('float64') 
	mask = df[df["EV"] >= j]
	print(len(mask))
	mask = mask[mask["Allocation Percentage"] >= 0]
	#print(mask)
	net = 0
	portfolio = start
	array = []
	for i in np.unique(mask.Date.values):
		new = mask[mask.Date == i]
		portnew = np.sum(new['Allocation Dollars']*new['Success']* new['Payouts (per Dollar)'])
		net = portnew - sum(new['Allocation Dollars'])
		array.append((portfolio+net)/portfolio)
		portfolio += net
		#print(net)
	if typing == 'array':
		return array
	else:
		return portfolio

def sim():
	sims = [check(i,'portfolio') for i in np.arange(1,1.3,0.001)]
	plt.plot(np.arange(1,1.3,0.001),sims)
	plt.show()
	return None

def counting():
	df = nba()
	dfs = df[df.EV>=1.05]
	print(len(df))
	for i in np.unique(dfs.Date.values):
		print(len(dfs[dfs.Date == i].values))
	return 'Done'
	
def winrate():
	df = nba()
	df = df[df.EV >1.05]
	array, wins, num = [], [], []
	for i in np.unique(df.Date.values):
		rate = np.mean(df[df.Date == i].Success.values)
		new = df[df.Date == i]
		num += [len(df[df.Date == i])]
		portnew = np.sum(new['Allocation Dollars']*new['Success']* new['Payouts (per Dollar)'])
		net = portnew - sum(new['Allocation Dollars'])
		wins += [net]
		array += [rate]
	print('Median win rate is:', np.median(array), ' mean is ', np.mean(array))	
	print('net per day', wins, np.unique(df.Date.values))
	sims = check(0,'array')
	print('Median win rate is:', np.median(sims), ' mean is ', np.mean(sims))
	plt.bar([i for i in range(len(array))],array)
	plt.show()
	return None
	
def nba():
	dfs = pd.read_csv('~/Desktop/sportsbook/BETATest/historicalBetLedger.csv')
	dfs['EV'] = [((dfs['Kelly Criterion Suggestion'].values[i]*dfs['Payouts (per Dollar)'].values[i] +1) / (dfs['Payouts (per Dollar)'].values[i]+1)) *dfs['Payouts (per Dollar)'].values[i] for i in range(len(dfs))]
	#dfs = dfs[dfs.Date>'2021-01-16']
	'''print(dfs['Success'].mean())'''
	Cap = sum(dfs['Allocation Dollars'])
	Ret = sum(dfs['Allocation Dollars']*dfs['Success']*dfs['Payouts (per Dollar)'])
	'''#print(dfs['EV'].mean())
	if Ret > 0:
		print((Ret-Cap)/Cap)
	#print(len(dfs))'''
	
	for i in np.unique(dfs.League.values):
		df = dfs[dfs.League == i]
		'''print(i)
		print(df['Success'].mean())
		print(df['EV'].mean())'''
		Cap = sum(df['Allocation Dollars'])
		Ret = sum(df['Allocation Dollars']*df['Success']*df['Payouts (per Dollar)'])
		'''if Ret > 0:
			print((Ret-Cap)/Cap)
		Ret = 0
			print(len(df))'''
	return dfs



def reading():
	df = pd.read_csv(os.getcwd() + '/538ELO.csv')	
	new = df.groupby(['raptor_prob1']).mean()
	print(new)
	return 'Done'

def getting():
  '''url = "https://projects.fivethirtyeight.com/2020-nba-predictions/games/"
  #print('hello')
  page_response = requests.get(url, timeout=10, headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
  page_content = BeautifulSoup(page_response.content, "html.parser")'''
  with open(os.getcwd() + '/rap.html') as f:
    html = f.read()
  page_content = BeautifulSoup(html, "html.parser")
  probs = [int(i.text[:-1])/100 for i in page_content.findAll('td', class_ = "td number chance")]
  one,two = [], []
  for i in page_content.findAll('div', class_ = "games-section extra-space-tablet extra-space-1"):
  	try:
  		one += [i.find('td', class_ = "td number score winner").text]
  		two += [' ']
  	except:
  		two += [i.find('td', class_ = "td number score loser").text]
  		one += [' ']
  gameScore = [one[k].strip()+two[k].strip() for k in range(len(one))]
  array = []
  for i in range(1,len(gameScore)):
  	if i%2 == 1:
  	  if int(gameScore[i])>int(gameScore[i-1]):
  	  	array += [0,1]
  	  else:
  	  	array += [1,0]
  print(len(probs),len(array))
  results = pd.DataFrame({'Probability':probs,'Success':array})
  results.to_csv(os.getcwd() + '/raptorPast.csv')
  print(results.groupby(['Probability']).mean())
  return 'Done'
#print(run())