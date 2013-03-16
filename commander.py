#!/usr/bin/python3

#GUI module of wallsan.py software

#Licensed under GNU General Public License Version 3

from re import search
from subprocess import Popen, PIPE, call
from configparser import ConfigParser
import tkinter
from tkinter.messagebox import showwarning
from tkinter.filedialog import askdirectory
import os.path
from os import chmod,chdir
from stat import S_IRWXU
from getpass import getuser


#This pipe is used to communicate with wallsan.py
global pipe_name
global wallProcessName
pipe_name = 'wallChangerPipe'

#send command stop
def commandStop():
	comm = open(pipe_name,'w')
	comm.write('stop')
	comm.close()

#send command resume:
def commandResume():
	comm = open(pipe_name,'w')
	comm.write('resume')
	comm.close()

#send command update:
def commandUpdate():
	comm = open(pipe_name,'w')
	comm.write('update')
	comm.close()

def checkProcess():
	#check if the wallchanger process is running in the OS
	#return True if running and False or else.
	wp = Popen('ps -e|grep wallsan.py',shell=True,stdout=PIPE)
	output = wp.stdout.read()
	wp.stdout.close()
	wp.wait()

	if search('wallsan.py',str(output)) is None:
		processRunning = False
	else:
		processRunning = True
	
	return processRunning


	
def updateConfig():
		dirname = direntry.get()
		interval = intervalEntry.get()
		try:
			interval1 = float(interval)
			isintfloat = True  #is interval entered is float
		except:
			isintfloat = False
		
		if os.path.isdir(dirname) and isintfloat:
			config2 = ConfigParser()
			config2['wallconfig'] = {'workingDirectory':dirname,
								'interval':interval,'state':'running'}

			with open('config.ini','w') as configFile:
				config2.write(configFile)
			#send update command to the wallchan processs
			commandUpdate()	
		else:
			showwarning('Wrong Input','Please check the input you have entered')

#================================================================================================
#---------      START THE INITIATION PROCESS    ----------


#changing the working directory to the location of the commander.py
chdir(os.path.dirname(os.path.realpath(__file__)))


processRunning = checkProcess()

if processRunning:
	pass
else:
   #Giving read write execute permissions to the owner
	#this allows us to call wallsan.py as an executable
	chmod('wallsan.py',S_IRWXU)
	Popen('./wallsan.py',stdin=None,stdout=None,stderr=None,close_fds=True)

#The GUI Interface
root = tkinter.Tk()
root.wm_title('WallSan')

frame1 = tkinter.Frame(root)
frame1.pack(side = tkinter.TOP)
frame2 = tkinter.Frame(root)
frame2.pack(side = tkinter.TOP)
frame3 = tkinter.Frame(root)
frame3.pack(side = tkinter.TOP)

#Textbox that takes wallpaper directory absolute path
direntry = tkinter.Entry(frame1)
direntry.pack(side = tkinter.LEFT)

#Function to initiate Browse directory
def browsedir():
	#defualtdir is the first directory the GUI shows while browsing for files 
	defaultdir = '/home/'+getuser()+'/Pictures'
	dirPath = askdirectory(title = 'Select wallpaper folder',mustexist=True,initialdir = defaultdir)
	direntry.delete(0,tkinter.END)
	direntry.insert(0,str(dirPath))
	direntry.pack(side = tkinter.LEFT)

#button that initates browsedir()
button1 = tkinter.Button(frame1, text = 'Browse Pictures',command = browsedir)
button1.pack(side = tkinter.LEFT)


label1 = tkinter.Label(frame2, text = 'Time Interval (seconds)')
label1.pack(side = tkinter.LEFT)
intervalEntry = tkinter.Entry(frame2)
intervalEntry.pack(side= tkinter.LEFT)


pauseButton = tkinter.Button(frame3,text = 'PAUSE',fg = 'RED', command = commandStop)
pauseButton.pack(side = tkinter.LEFT)
resumeButton = tkinter.Button(frame3, text = 'RESUME', fg = 'BLUE', command = commandResume)
resumeButton.pack(side = tkinter.LEFT)
updateButton = tkinter.Button(frame3, text = 'UPDATE', fg = 'BLUE', command = updateConfig)
updateButton.pack(side = tkinter.LEFT)

root.mainloop()
#GUI is initiated
