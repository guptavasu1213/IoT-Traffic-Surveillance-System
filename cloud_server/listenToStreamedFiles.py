import os
import signal

# Flags for handlers
numVideosToAnalyze = 0
terminate = False

def processVideos(signum, stack):
	'''
	Signal handler for receiving a signal to process video files
	'''
	# print('YAYYYYYY:', signum)
	global numVideosToAnalyze
	numVideosToAnalyze += 1

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

def listenToReceivedFiles(folderPath):
	'''
	To listen to the folder with received files, this process communicates with the parent
	process and receives signal from it whenever
    '''
	# Setup handlers
	signal.signal(signal.SIGUSR1, processVideos)
	signal.signal(signal.SIGINT, terminateProcess)
	global numVideosToAnalyze

	print('My PID is:', os.getpid())

	#Send a ready signal to the parent process
	os.kill(os.getppid(), signal.SIGUSR2)

	while True:
		print("SLEEP----------------------")
		signal.pause()
		print("WOKEUP---------------------")
		# if numVideosToAnalyze > 0:
		while numVideosToAnalyze > 0:
			videoFiles = os.listdir(folderPath)
			if len(videoFiles) == 0 : break
			videoFile = sorted(videoFiles)[0]
			print("Analyzing file: ", videoFile)

			#Removing file after analysis
			os.remove(os.path.join(folderPath, videoFile))
			numVideosToAnalyze -= 1

		if terminate:
			print("Terminating video now", "=" * 8)
			exit(0)
