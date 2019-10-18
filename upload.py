import boto3
import time
import subprocess
#################  This function uploads the supplied html file to the server at the home location,
#################  It uses the same key supplied in the run program to scp the file to the server
#################  this is to connect to my ubuntu server
def htmlUpload(ipAddress, key):
	myupload = 'scp -i '+key+'.pem -o StrictHostKeyChecking=no index.html ubuntu@'+ipAddress+':.'
   
	try:
		print("\n------Check upload html------\n")
		print(subprocess.run(myupload, shell = True,check = True))

	except:
		print("\nHtml Upload failed!!!")
	return;
##################  This is my variable wait function/loop that is used throughout the program
def waitTime(t):
	while t!=0:
		print("waiting "+str(t)+" seconds")
		time.sleep(1.0)
		t=t-1
	return;

#################  This function takes in the ip address and the key, it then delets the original html file for the NginX server and replaces it with my own
#################  The html file is hardcoded with the address that the file will be at when created in the S3 bucket
#################  The image that it pulls from the s3 buck will be displayed as the background of the webpage 
def moveRestart(ipAddress, key):
	mymoveDeleteandrestart = "ssh -i "+key+".pem ubuntu@"+ipAddress+" 'cd /var/www/html; sudo rm *; cd ~; sudo mv index.html /var/www/html/index.html; sudo service nginx stop; sudo service nginx start'"
	try:
		print("\n------Check setup------\n")
		print(subprocess.run(mymoveDeleteandrestart, shell = True,check = True))

	except:
		print("\nMove of index.html and restart of nginx failed... ")
	return;

