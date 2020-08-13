'''
This file listens to the videos received by the server by the fog node and analyze the received videos.
'''
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-fp", "--folderPath", help="folder path of streamed camera videos", required=True)
args = vars(ap.parse_args())

import os
import signal

from main_live_stream import *


# Flags for handlers
numVideosToAnalyze = 0
terminate = False
ppid = 0

def processVideos(signum, stack):
	'''
	Signal handler for receiving a signal to process video files
	'''
	global numVideosToAnalyze
	numVideosToAnalyze += 1
	# print('YAYYYYYY:', numVideosToAnalyze)
	os.kill(ppid, signal.SIGUSR1)

def terminateProcess(signum, stack):
	'''
	Signal handler for termination of the current process
	'''
	# If video analysis is ongoing, then set the terminate flag to True
	if numVideosToAnalyze > 0:
		global terminate
		terminate = True
	else:  # Terminating when there is no ongoing video analysis
		# print("QUITTING")
		exit(0)

def getFogAndCameraName(videoFilePath):
	'''
	Extracting the fog node name and the camera name from the file path
	:param videoFilePath: Path to the video file
	:return: Camera name, Fog Node name
	'''
	videoFilePath += "/"
	splittedPath = videoFilePath.split("/")
	if splittedPath[-1] == "":
		return splittedPath[-3], splittedPath[-4]
	else:
		return splittedPath[-2], splittedPath[-3]

def sortFiles(fileList):
	'''
	:param fileList: List of file names which are of the form "<integer>.<extension>"
	'''
	sortedFilesWithoutExtension = dict()
	for file in fileList:
		sortedFilesWithoutExtension[(int(file.split(".")[0]))] = file

	sortedFiles = []
	for file in sorted(sortedFilesWithoutExtension):
		sortedFiles.append(sortedFilesWithoutExtension[file])
	return sortedFiles

def main_listen():
	'''
	To listen to the folder with received files, this process communicates with the parent
	process and receives signal from it whenever
    '''
	global ppid
	ppid = os.getppid()
	folderPath = args["folderPath"]

	# Setup handlers
	signal.signal(signal.SIGUSR1, processVideos)
	signal.signal(signal.SIGINT, terminateProcess)
	global numVideosToAnalyze

	print('My PID is:', os.getpid())

	#Send a ready signal to the parent process
	os.kill(ppid, signal.SIGUSR2)
	print("===================================================READY SENT")
	while True:
		print("SLEEP----------------------")
		signal.pause()
		print("WOKEUP---------------------", numVideosToAnalyze)
		while numVideosToAnalyze > 0:
			# print("VIDEOS TO ANA:", numVideosToAnalyze)
			videoFiles = os.listdir(folderPath)
			sortedFiles = sortFiles(videoFiles)
			videoFile = sortedFiles[0]
			print("Analyzing file: ", videoFile)
			videoAbsPath = os.path.abspath(os.path.join(folderPath, videoFile))
			print("ABS:", videoAbsPath)
			cameraName, fogNodeName = getFogAndCameraName(videoAbsPath)
			# print("Cam:" , cameraName, "Fog:", fogNodeName)
			main(videoAbsPath)

			# countVideo(videoAbsPath, fogNodeName, cameraName)
			#Removing file after analysis
			os.remove(videoAbsPath)
			numVideosToAnalyze -= 1

		if terminate:
			print("Terminating video now", "=" * 8)
			exit(0)
main_listen()