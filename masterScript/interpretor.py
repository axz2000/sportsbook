import iterations
#import decisiontree
import subprocess

def dailyReturn():
	iterations.run()
	decisiontree.run()
	return 'Update finished and classification completed'

def pushing():
	subprocess.Popen("git add --all; git commit -m 'Update'; git push", shell = True)
	return 'Git Push Done'		

'''
To do:
-- comment some more stuff and figure out hwo to implement NHl in this exact framework, maybe jsut replace the XHR, but the bettting is different, run seperately?
-- add over under, period bets, make the names for tie more clear if possible
-- make tree structure easy to implement

Notes:
-- this will force people to make a directory or maybe to have a folder called data in place, thinking of possible easy of application
'''

#Make a time function
print('Updates for the day.')
print(dailyReturn())


	
