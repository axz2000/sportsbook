from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np 

from IPython.core.display import display, HTML

from sklearn import preprocessing, tree
from dtreeviz.trees import dtreeviz

from matplotlib import pyplot as plt

import pandas as pd

df1 = pd.read_csv('./betLedger.csv')
df1 = df1[['Bet State Chosen', 'Kelly Criterion Suggestion', 'Payouts (per Dollar)', 'League','Success']]
df1['Success'] = ['Yes' if i==1.0 else 'No' for i in df1.Success.values]

print(df1)
Things = {'Feature01': df1['Payouts (per Dollar)'].values, 
          'Feature02': df1['Kelly Criterion Suggestion'].values, 
          'Target01': df1['Success'].values}
          
df = pd.DataFrame(Things,
                  columns= ['Feature01', 'Feature02','Target01' ]) 

label_encoder = preprocessing.LabelEncoder()
label_encoder.fit(df.Target01)
df['target'] = label_encoder.transform(df.Target01)

classifier = tree.DecisionTreeClassifier()
classifier.fit(df.iloc[:,:2], df.target)

viz = dtreeviz(classifier,
         df.iloc[:,:2],
         df.target,
         target_name='toy',
         feature_names=df.columns[0:2],
         class_names=list(label_encoder.classes_)
         )

display(HTML(viz.svg()))