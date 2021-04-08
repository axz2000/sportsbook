import iterations
import decisiontree
import simultaneousKelly
import subprocess

def dailyReturn():
	inputs = input("Are you here to update? ").lower()
	if inputs == 'yes':
		iterations.run(inputs)
		return 'Update finished'
	else:
		iterations.run(inputs)
		decisiontree.run()
		simultaneousKelly.run()
		pushing()
		return 'Update finished and classification completed'

def pushing():
	subprocess.Popen("git add --all; git commit -m 'Update'; git push;", shell = True)
	return 'Git Push Done'		

print('Updates for the day.')
print(dailyReturn())


	
