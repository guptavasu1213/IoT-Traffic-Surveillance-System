'''
This file listens to the videos received by the server by the fog node and analyze the received videos.
'''
import argparse
import os

ap = argparse.ArgumentParser()
ap.add_argument("-fp", "--folderPath", help="folder path of streamed camera videos", required=True)
args = vars(ap.parse_args())

# Error check the folder path
folderPath = args["folderPath"].strip()
if not os.path.isdir(folderPath):
	print("ERROR: The specified folder path is invalid")
	exit(1)

import signal

from main_live_stream import *
from calculate_encoding import calculate_encoding_params

# Flags for handlers
numVideosReceived = 0
terminate = False
ppid = 0
videoNumToStartEncoding = None

VIDEO_LENGTH = 1 #SEC
ENCODING_COMPUTATION_TIME = 3 #SEC
NUM_VIDEOS_FOR_ENCODING = round(ENCODING_COMPUTATION_TIME/VIDEO_LENGTH)

def processVideos(signum, stack):
	'''
	Signal handler for receiving a signal to process video files
	'''
	global numVideosReceived
	numVideosReceived += 1
	# print('YAYYYYYY:', numVideosToAnalyze)
	os.kill(ppid, signal.SIGUSR1)

def signalEncodeParams(signum, stack):
	global videoNumToStartEncoding
	videoNumToStartEncoding = numVideosReceived

def terminateProcess(signum, stack):
	'''
	Signal handler for termination of the current process
	'''
	# If video analysis is ongoing, then set the terminate flag to True
	if numVideosReceived > 0:
		global terminate
		terminate = True
	else:  # Terminating when there is no ongoing video analysis
		# print("QUITTING")
		exit(0)

def getFogAndCameraName(folderPath):
	'''
	Extracting the fog node name and the camera name from the file path
	:param videoFilePath: Path to the video file
	:return: Camera name, Fog Node name
	'''
	folderPath += "/"
	splittedPath = folderPath.split("/")
	if splittedPath[-1] == "":
		return splittedPath[-2], splittedPath[-3]
	else:
		return splittedPath[-1], splittedPath[-2]

def getLineCoordinatesFileName():
	'''

	'''
	lastSlashIndex = folderPath.rfind("/")
	if lastSlashIndex == len(folderPath)-1:
		lastSlashIndex = folderPath[:-1].rfind("/")
	return folderPath[:lastSlashIndex+1] + "line_coordinates.txt"

def getCountLogFilePath(cameraName, fogNodeName):
	'''

	'''
	index = folderPath.find("streamed_files")
	return os.path.join(folderPath[:index], "detection_logs", fogNodeName, cameraName, "log.txt")

def getEncodedVideoFolderPath(cameraName, fogNodeName):
	index = folderPath.find("streamed_files")
	return os.path.join(folderPath[:index], "encoding_videos", fogNodeName, cameraName)

def getLineCoordinatesForCamera(cameraName, fogNodeName):
	'''
	Extracts the line(s) coordinates for the given fog node and the camera
	fileName: The file name of the video
	'''
	#Open line coordinates file
	with open(getLineCoordinatesFileName()) as file:
		coordinatesFile = file.read()

	cameraIndex = coordinatesFile.find(cameraName)
	newlineIndex = coordinatesFile.find('\n', cameraIndex)

	if cameraIndex == -1:
		print("No line_coordinates found")
		return False

	lineInFile = coordinatesFile[cameraIndex:newlineIndex]
	lines = lineInFile[lineInFile.find(':')+1:]
	return lines
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

def get_video_resolution(videoPath):
	'''

	'''
	import tempfile
	import re

	tmpf = tempfile.NamedTemporaryFile()
	os.system("ffmpeg -i \"%s\" 2> %s" % (videoPath, tmpf.name))
	lines = tmpf.readlines()
	tmpf.close()
	for line in lines:
		line = line.decode('UTF-8').strip()
		if line.startswith('Stream #0:0'):
			resolution = re.search('([1-9]\d+x\d+)', line).group(1)
			return [int(val) for val in resolution.strip().split('x')]

import time
def dummySleep(max_time):
	st = time.time()
	while time.time() - st < max_time:  # Goes through the loop for the specified time
		continue

def main_listen():
	'''
	To listen to the folder with received files, this process communicates with the parent
	process and receives signal from it whenever
    '''
	global ppid, folderPath, numVideosReceived, videoNumToStartEncoding
	ppid = os.getppid()
	numVideosAnalyzed = 0
	resolution = None

	folderPath = os.path.abspath(folderPath)
	cameraName, fogNodeName = getFogAndCameraName(folderPath)
	count_file_path = getCountLogFilePath(cameraName, fogNodeName)
	encoding_folder_path = getEncodedVideoFolderPath(cameraName, fogNodeName)
	line_coordinates = getLineCoordinatesForCamera(cameraName, fogNodeName)

	# Setup signal handlers
	signal.signal(signal.SIGUSR1, processVideos)
	signal.signal(signal.SIGUSR2, signalEncodeParams)
	signal.signal(signal.SIGINT, terminateProcess)

	print('*****************My PID is:', os.getpid(), "PPID is:", ppid, "*****************")

	sortedFiles = []

	#Send a ready signal to the parent process
	os.kill(ppid, signal.SIGUSR2)
	print("===================================================READY SENT")
	while True:
		# print("SLEEP----------------------")
		signal.pause()
		print("WOKEUP---------------------", numVideosReceived)
		while numVideosAnalyzed < numVideosReceived:
			if sortedFiles == []: # Creating a list of files in sorted order
				videoFiles = os.listdir(folderPath)
				sortedFiles = sortFiles(videoFiles)

			videoFile = sortedFiles.pop(0) #Retreive the next file to analyze
			print("Analyzing file: ", videoFile)
			videoAbsPath = os.path.abspath(os.path.join(folderPath, videoFile))
			start_vid_num = videoNumToStartEncoding #Global variable can change, so create a local copy

			###########ALSO, CHANGE RESOLUTION WHEN RECEIVE A VIDEO WITH NEW ENCODING PARAMS

			# If the video is the first to be encoded
			if numVideosAnalyzed+1 == start_vid_num:
				# Storing the counts before initializing the framework
				write_count(count_file_path)

				print("CALCULATE ENCODING NOW with FIRST", videoFile, "========")

				# Initializing the framework
				resolution = get_video_resolution(videoAbsPath)
				initialize_vars(line_coordinates, resolution)

				#Removes all files in the encoding folder (if any)
				fPath = os.path.join(encoding_folder_path, "videos")
				if len(os.listdir(fPath)):
					os.system("rm {}/*.mp4".format(fPath))

			# Perform vehicle counting
			main(videoAbsPath)

			if 	numVideosAnalyzed+1 >= start_vid_num and \
				numVideosAnalyzed+1 <=  start_vid_num + NUM_VIDEOS_FOR_ENCODING-1:
				print("IN RANGE with", videoFile, "========")

				# Move the video to the encoding folder
				os.rename(videoAbsPath, os.path.join(encoding_folder_path, "videos", videoFile))

				if numVideosAnalyzed+1 ==  start_vid_num + NUM_VIDEOS_FOR_ENCODING-1:
					# if at the last video, compute the encoding parameters
					print("LAST with", videoFile, "========")

					high_resolution_count = 100################
					calculate_encoding_params(encoding_folder_path, high_resolution_count)

					os.kill(ppid, signal.SIGABRT)

			else:
				print("NORMAL ANALYSIS", videoFile)
				dummySleep(1)

				#Removing file after analysis
				os.remove(videoAbsPath)
			numVideosAnalyzed += 1

		# numVideosAnalyzed, numVideosReceived = 0, 0 #Reset variables
		if terminate:
			print("Terminating video now", "=" * 8)
			exit(0)
main_listen()