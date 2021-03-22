from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np 
from sklearn import preprocessing, tree
import pandas as pd

def run():
	df1 = pd.read_csv('./historicalBetLedger.csv')
	df1 = df1[['Bet State Chosen', 'Kelly Criterion Suggestion', 'Payouts (per Dollar)', 'League','Success','Date','Allocation Percentage']]
	df1['Success'] = ['Yes' if i==1.0 else 'No' for i in df1.Success.values]

	Things = {'Feature01': df1['Payouts (per Dollar)'].values, 
          'Feature02': df1['Kelly Criterion Suggestion'].values, 
          'Target01': df1['Success'].values}
          
	df = pd.DataFrame(Things,
                  columns= ['Feature01', 'Feature02','Target01' ]) 

	label_encoder = preprocessing.LabelEncoder()
	label_encoder.fit(df.Target01)
	df['target'] = label_encoder.transform(df.Target01)

	X_train, y_train = df[['Feature01', 'Feature02']], df.target

	classifier = tree.DecisionTreeClassifier()
	classifier.fit(X_train, y_train)

	picks = pd.read_csv('./masterUpcoming.csv')
	todaysPicks = pd.DataFrame({'Feature01':picks['Payouts (per Dollar)'].values, 'Feature02':picks['Kelly Criterion Suggestion'].values})
	today = classifier.predict(todaysPicks) == 1
	(picks[today]).to_csv('./masterUpcoming.csv')
	return 'Classification Done'

print(run())

