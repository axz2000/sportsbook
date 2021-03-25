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
	return matches

def Kelly(oddsDecimal, probability):
  return (oddsDecimal*probability - (1-probability))/oddsDecimal

def reverseKelly(payout, Kelly):
	return( (kelly * payout -1)/(1+payout) )

def reverseOdds(dec):
	if dec>2:
		val = (dec - 1)*100
		return "+" + str(int(val))
	else:
		val = 100/(dec - 1)
		return "-" + str(int(val))
	
def powerLaw(df):
  kelly = df['Kelly Criterion Suggestion'].values
  allocation1 = [np.median(kelly)*(i/np.sum(kelly)) for i in kelly] #RISK TOLERANCE ESTABLISHED HERE 
  df['Allocation Percentage'] = allocation1
  return df

def gainsLosses(allocation,successes, df, portfolio):
  payouts = df['Payouts (per Dollar)'].values
  prev = np.sum(allocation)
  now = np.sum(np.dot([allocation[i]*payouts[i] for i in range(len(payouts))], successes))
  return [portfolio+(now-prev), prev, now]

def oddstoPayout(odds,dollarsIn):
  if odds<0:
    multiplier = 1/(abs(odds/100))
    return dollarsIn + dollarsIn*multiplier
  else:
    multiplier = odds/100
    return dollarsIn + dollarsIn*multiplier

		
def dailyReturn():
	dataFrame = pd.read_csv('./MMALookBackValueSystem.csv')
	'''dataFrame['Odds'] = [oddstoPayout(int(dataFrame.Odds.values[i]),1) for i in range(len(dataFrame.Odds.values))]
	dataFrame['EV'] = [dataFrame.Odds.values[i]*dataFrame.Probabilities.values[i] for i in range(len(dataFrame.Odds.values))]
	dataFrame = dataFrame[dataFrame.EV >=1.07]
	dataFrame['Kelly'] = [Kelly(dataFrame.Odds.values[i],dataFrame.Probabilities.values[i]) for i in range(len(dataFrame.Odds.values))]
	dataFrame['Winner'] = [re.sub('\s+', '', i) for i in dataFrame.Winner]
	dataFrame.to_csv('./MMALookBackValueSystem.csv') #PREPROCESSING'''
	print(dataFrame)
	allocationArray  = []
	summing = 0
	wonwon, sumsum = 0,0
	sums = []
	for i in np.unique(dataFrame.Date.values):
		df = dataFrame[dataFrame.Date == i]
		kelly = df['Kelly'].values
		allocation1 = [0.1*i for i in kelly] #RISK TOLERANCE ESTABLISHED HERE 
		df['Allocation Percentage'] = allocation1
		allocationArray += allocation1
		spent = np.sum(allocation1)
		masking = []
		for i in df.Winner:
			if i == 'Winner':
				masking += [1]
			else:
				masking += [0]
		won = np.sum([allocation1[i]*masking[i]*df.Odds.values[i] for i in range(len(df))])
		sumsum += spent
		wonwon += won
		summing += (won - spent)
		sums += [won-spent]
	print(summing, sums, wonwon/sumsum, np.mean(dataFrame.EV.values),len(dataFrame))
	return 'Done'
	
		
		
	
def dailyPayouts():
	dataFrame = pd.read_csv('./MMALookBackValueSystem.csv')
	Payouts = [oddstoPayout(int(i),1) for i in dataFrame.Odds]
	dataFrame['Odds'] = Payouts
	dataFrame.to_csv('./MMALookBackValueSystem.csv')
	
	


'''
To do:
-- comment some more stuff and figure out hwo to implement NHl in this exact framework, maybe jsut replace the XHR, but the bettting is different, run seperately?
-- add over under, period bets, make the names for tie more clear if possible
-- make tree structure easy to implement

Notes:
-- this will force people to make a directory or maybe to have a folder called data in place, thinking of possible easy of application
'''

#Make a time function

print(dailyReturn())


	
