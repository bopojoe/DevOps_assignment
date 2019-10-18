import subprocess
myFunc = 'ps -A |grep nginx'
myStartFunc = 'sudo service nginx start'
try:
	subprocess.run(myFunc,shell = True,check = True, stdout = subprocess.PIPE)
	print("Up,UP and away cap'n")
except:
	print("Black Hawk DOWN!!!")
	print("Starting Nginx now ")
	subprocess.run(myStartFunc,shell = True,check = True, stdout = subprocess.PIPE)
	try:
		subprocess.run(myFunc,shell = True,check = True, stdout = subprocess.PIPE)
		print("Up,UP and away cap'n")
	except:
		print("that didn't work")
