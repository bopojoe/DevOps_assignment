#!/usr/bin/env python3
import sys
import webbrowser
import boto3
import time
import subprocess
import upload

##  -----Key and Security group assignment variables----- 
key = sys.argv[1]
sGroup = sys.argv[2]

##  -----S3 bucket setup for Bucket name and supplied picture name----- 
s3 = boto3.resource("s3")
bucket_name = sys.argv[3]
object_name = sys.argv[4]

## ------create index.html for server------------------

hrefLink = "https://s3-eu-west-1.amazonaws.com/"+bucket_name+'/'+object_name

address = '<a style="color:red; text-align:center; font-size:400%;" href = "'+hrefLink+'">'+hrefLink+'</a>'


htmlfile = open("index.html", "w+")

htmlfile.write('<html>\n<body background='+hrefLink+'>\n<h1 style="color:red; text-align:center;">Hi Richard and Jimmy!</h1\n<p style="color:black; text-align:center;">Hopefully all this worked and you can see this!!</p>\n<br /><br />\n<br /><br />\n<br /><br />\n<br /><br />\n<br /><br />\n'+address+'\n</body>\n</html>')


htmlfile.close()

##  -----ec2 instance setup using the ubuntu ami and the supplied key and security groups-----
##  -----It also supplies the user data needed to install and start the Default NginX server------
ec2 = boto3.resource('ec2')
instance = ec2.create_instances(
    ImageId='ami-00035f41c82244dab',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName = key,
    SecurityGroups=[sGroup],
    UserData="""#!/bin/bash
                sudo apt -y update
		sudo apt -y install python3
                sudo apt -y install nginx
                sudo service nginx start""")

inst = instance[0]
idString = str(instance[0].id)

tagName = input("Please give the instance a name ==> ")



print ("--------Waiting on instance to boot--------")
print ("\n--------This can take about 30 seconds--------")

inst.wait_until_running()

##  -----loop that prints the id's and ip addresses of any running instances----- 
##  -----This can break the program if they're are other running instances-----

instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
for i in instances:
    inst = i
    print("\nInstance Id: "+i.id+", Instance IP Address: "+i.public_ip_address)

## ------------------ set instance tag ---------------
try:
	ec2.create_tags(Resources=[idString,], Tags=[{'Key':'Name', 'Value':tagName}])
	print("\nThe instance was tagged with the Name: "+tagName)
except:
	Print("\nThe tag for the instance failed!!!")


## -----setup for all the commands i run in the program, the first one is just for the -o command to add server to Known Hosts-----
mySshtest = 'ssh -i '+key+'.pem -o StrictHostKeyChecking=no ubuntu@'+inst.public_ip_address +" 'ls'"

myScp = 'scp -i '+key+'.pem -o StrictHostKeyChecking=no check_webserver.py ubuntu@'+inst.public_ip_address +':.'

mySshrunCheck = 'ssh -i '+key+'.pem ubuntu@'+inst.public_ip_address +" 'python3 check_webserver.py'"

## -----This wait is for the server to complete its original tasks ----- 
upload.waitTime(10)

## ----- This is the first subProcess command that runs the -o command -----
try:
	print("\n---------Doing sshtest for yes command---------")
	print(subprocess.run(mySshtest, shell = True,check = True))
	print("\nIP Address now added to trusted")
except:
	print("\nssh failed, Program Will Fail!!!")
## ----- This is the scp subProcess command for the check_webserver.py file -----
try:
	print("\n---------Running Scp Command---------")
	print(subprocess.run(myScp, shell = True,check = True))
	print("\nFile transfer in progress")
except:
	print("\nError running scp command for Check_webserver!!!")
## ----- This wait is to ensure the server is actually ready to run the check_webserver file and also to make sure its ready for command line input -----
upload.waitTime(20)

## ----- This subProcess runs the check_webserver file and prints the output to the user -----
try:
	print("\n---------Check Webserver---------\n")
	output = subprocess.run(mySshrunCheck, shell = True,check = True, stdout = subprocess.PIPE)
	print(output)
	print("\n--------Standard NginX server running--------")

except:
	print("\nCheck web Server command failed!!!")

## ----- This is the start of the S3 bucket setup -----

## ----- This trys to create the bucket with the hardcoded name I supplied at the top of the file -----
try:
    response = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
    print ("\n--------New Bucket Created called '"+bucket_name+".s3-eu-west-1.amazonaws.com' --------")
except Exception as error:
    print (error)

## ----- This section trys to upload the supplied Picture to the bucket and then set it's permissions to public so it can be read by other users  -----
try:
    response = s3.Object(bucket_name, object_name).put(Body=open(object_name, 'rb'), ContentType='i')
    print ("\n--------New Photo Uploaded at '"+bucket_name+".s3-eu-west-1.amazonaws.com/"+object_name+"' --------")
    object = s3.Bucket(bucket_name).Object(object_name)
    object.Acl().put(ACL='public-read')
except Exception as error:
    print (error)

## ----- This is Bulk of the use from the upload.py file  -----

## ----- This function takes the IP address and key name, it then passes it to the function to upload the html file supplied to the nginx server home directory  -----
upload.htmlUpload(inst.public_ip_address,key)

## ----- This wait is for the file upload process -----
upload.waitTime(5)

## ----- This function takes the same inputs but uses the ssh command to send arguments to the server -----
## ----- > it moves to the default nginx html file location  -----
## ----- > it removes all the files from the location -----
## ----- > it returs to the home directory -----
## ----- > it moves the index.html file to the nginx html folder -----
## ----- > it then restarts the nginx server so it loads the new html file -----
upload.moveRestart(inst.public_ip_address, key)

## ----- This opens the firefox browser and opens the website created ----- 
print("\n-------- Opening firefox to display the website at "+inst.public_ip_address+" --------")
webbrowser.get('firefox').open_new_tab(inst.public_ip_address)

print("\n--------The Program Has Now Finished--------\n")

print("--------Thank You--------")









