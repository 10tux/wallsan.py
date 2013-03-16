#!/usr/bin/python3

#wallpaper changing module of wallsan software

#Licensed under GNU General Public License Version 3

#importing the required functions from python standard libraries
from subprocess import call
from os import listdir,mkfifo,chdir
from os.path import isfile, isdir, join, splitext,exists,dirname,realpath
from getpass import getuser
from multiprocessing import Process
from time import sleep
from random import randrange
from configparser import ConfigParser



#===============================================================================


def configRead():
	#Read the config file and set the variables
	#Open communication on a named_pipe

	
	try:
		config1 = ConfigParser()
		config1.read('config.ini')
		workingDir = config1['wallconfig']['workingDirectory']
		interval = config1['wallconfig']['interval']
		state = config1['wallconfig']['state']
			
	except:
		#write a new config file, with default values			
		workingDir = '/home/'+getuser()+'/Pictures'
		interval = 5  #5seconds
		state = 'running'
		config2 = ConfigParser()
		config2['wallconfig'] = {'workingDirectory':workingDir,
							'interval':interval,'state':state}
							
		with open('config.ini','w') as configFile:
			config2.write(configFile)
	#return the config values
	return (workingDir,interval,state)	



#updates the config.ini file whenever the state of the program is paused / kept as running
def toggleState(configList,state):
	config2 = ConfigParser()
	config2['wallconfig'] = {'workingDirectory':configList[0],
							'interval':configList[1],'state':state}
	
	with open('config.ini','w') as configFile:
		config2.write(configFile)



#Takes a directory as input and gives the list of paths of supported image files
def readDirectory(dir_name,picExtension):
	
	imageFiles = []  #Initiating an empty list of image files
	
	#Iteratively go through the list of files
	
	if isdir(dir_name):	
		for f in listdir(dir_name):
			filePath = join(dir_name,f)
			
			if isfile(filePath):
				fileExt = splitext(filePath)[1]			
				#Get the files extension and check if it is a valid image file	
				#Add the image path to the list	
				if any(item == fileExt for item in picExtension):
					imageFiles = imageFiles+[filePath]
	else:
		raise IOError
	#returns the list of image files			
	return imageFiles
	
#===============================================================================

def changeWallpaper(picPath):
	#Call the mate configuration tool to change wallpaper
	#you can replace this command with gnome/kde/xfce etc.. config commands if available
	if isfile(picPath):
		call(['mateconftool-2','-t','string','-s','/desktop/mate/background/picture_filename',picPath])
	else:
		print('File Not Found')
		raise IOError



def randWallpaper(imagelist):
	#picks a random wallpaper from the list and set it as wallpaper
	
	length = len(imagelist)
	if length == 1:
		index = 0
	else:
		index = randrange(0,len(imagelist))
	
	changeWallpaper(imagelist[index])



def wallchangerLoop(dir_name,fileExtensions,timeInterval):
#sets random image as the wallpaper at repeated intervals
	while True:
		imagelist = readDirectory(dir_name,fileExtensions)
		if len(imagelist) == 0:
			sleep(5) #waits for 5 seconds and reads directory again in search of image files.
			continue
		try:
			randWallpaper(imagelist)
		except IOError:
			imagelist = readDirectory(dir_name,fileExtensions)
		except:
			break
		sleep(float(timeInterval)) #wait for some seconds and continue 

#===============================================================================

def commandLoop(fileExtensions,pipe_name,configList):
	state = configList[2]
	if(state == 'paused'):
		pass
	else:
		#starting the wallchangerLoop which runs as a seperate process continuously changing wallpapers
		wallChanger = Process(target = wallchangerLoop, args = (configList[0],fileExtensions,configList[1]),name = 'wallloop')	
		wallChanger.start()  
	while True:
	#opening the named pipe in read mode
	#receives commands from the GUI/Controller
		commander = open(pipe_name,'r')
		command = commander.read()
		commander.close()
		print(command)
		# check if the wallChanger loop is running and assign
		# appropriate state to the state variable
		try:
			if wallChanger.is_alive():
				state = 'running'
			else:
				state = 'paused'
		except UnboundLocalError:
			#If the program in started in pause mode, and resumed with GUI the WallChanger
			#is not yet initialized, hence calling is_alive() raises an exception which is catched.
			wallChanger = Process(target = wallchangerLoop, args = (configList[0],fileExtensions,configList[1]),name = 'wallloop')	
			state = 'paused'	

		if(command == 'stop' and state == 'running'):
		#stop the wall loop process
			wallChanger.terminate()
			wallChanger.join()
			state = 'paused'
			toggleState(configList,state)
		elif(command == 'resume' and state == 'paused'):
			#start the wall loop process
			wallChanger = Process(target = wallchangerLoop, args = (configList[0],fileExtensions,configList[1]),name='wallloop')	
			wallChanger.start()
			state = 'running'
			toggleState(configList,state)			
		elif(command == 'update'):
			#re-read the config file and restart the process
			
			if(state == 'running'):
			#if the process is still alive, kill the process
				wallChanger.terminate()
				wallChanger.join()
			
			configList = configRead()
			wallChanger = Process(target = wallchangerLoop, args = (configList[0],fileExtensions,configList[1]),name='wallloop')
			wallChanger.start()
		

		
#===============================================================================

	#****************************************
	#**         STARTUP SEQUENCE           **
	#****************************************
	

#valid image file extensions, you can add other formats, if system supports it
fileExtensions = '.jpg','.jpeg','.png','.svg','.bmp','.tiff','.gif','.raw'

#changing the working directory to the wallsan.py directory
chdir(dirname(realpath(__file__)))

pipe_name = 'wallChangerPipe'	#name of the pipe that recives commands from the GUI
#Get the configuration variables
configList = configRead()

#check if the pipe exists. If it doesn't exist, create it.
if exists(pipe_name):
	pass
else:
	mkfifo(pipe_name)


commandLoop(fileExtensions,pipe_name,configList)
