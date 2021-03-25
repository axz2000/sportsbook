import pandas as pd
from googlesearch import search
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
import internal
from nltk import tokenize
from operator import itemgetter
import math
from matplotlib import pyplot as plt 

'''
plt.plot([153, 543.4618870557283, 263.21320672411343, 640.1263118463205, 1075.484403815292, 1018.4019003092046, 2673.465211492394, 1473.3617101846999, 2640.998409526059, 5874.5515611232895, 12067.737558747362, 28523.923754594416, 18580.790201922042, 7671.8996992795655, 13939.550415436943, 6039.924750441667, 5038.517244198675, 2019.1220420403688, 2064.1542021582954, 2460.4930507484705, 2771.96060684822, 3383.562308563064, 4269.642840463632, 4577.2367557633725, 4423.418729693156, 3475.9295067144812, 4593.990762630443, 1584.6591353381918, 2480.0875405835386, 2721.688596957041, 1955.0907465252408, 3061.197897033298, 1008.17444201646, 639.7065503139962, 614.3091013625087, 395.3411782757329, 664.248541089185, 700.1597389599538, 527.0380261882256, 500.3789389080964, 543.559679965073, 533.0664074655092, 607.084014855196, 870.6958522355163, 1131.320742859206, 867.835092945626, 122.98725810978794, 111.95350377632224, 67.33577317988599, 103.91095872260098, 79.35789272300364, 146.05172213419013, 52.52307637030658, 31.207375104809806, 35.280297556933164, 7.465027627402264, 11.051452956905795, 15.834171721146985, 10.681353193959996, 8.458739450367958, 6.46428245268591, 4.383105842175253, 4.933074673659956])
plt.yscale("log")
plt.show()'''
print(internal.simKelly())

'''
upcoming = pd.read_csv('masterDailyRecap.csv')
#print(upcoming)
query = "NBA Game Score Today Grizzlies FlashScore"
my_results_list = []
for i in range(0,1): #len(upcoming)
	league = upcoming.League.values[i]
	team = upcoming['Bet State Chosen'].values[i]
	query = league + 'game score today' + team + ' flashscore'
	print(query)
	for i in search(query,        # The query you want to run
                tld = 'com',  # The top level domain
                lang = 'en',  # The language
                num = 1,     # Number of results per page
                start = 0,    # First result to retrieve
                stop = 1,  # Last result to retrieve
                pause = 0.5,  # Lapse between HTTP requests
               ):
		my_results_list.append(i)

page_response = requests.get(my_results_list[0], timeout=10, headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
page_content = BeautifulSoup(page_response.content, "html.parser")
print(page_content)
print(my_results_list[0])'''