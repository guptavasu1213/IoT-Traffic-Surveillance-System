# from listenToStreamedFiles import *

import os
import signal
import subprocess

# Handler flags
listening = False
receiveMoreVideos = False
sendEncodingParams = False

def listeningProcessReady(signum, stack):
	'''
	Signal handler to specify that the child process is ready to listen
	'''
	global listening
	listening = True

def listeningProcessReceivedVideo(signum, stack):
	'''
	Signal handler to specify that the child process has received the video
	'''
	global receiveMoreVideos
	receiveMoreVideos = True

def receiveEncodingParams(signum, stack):
	'''

	'''
	global sendEncodingParams
	sendEncodingParams = True

def receiveAcknowlegdement(socket, message="OK"):
	'''
	This function waits to receive a message at the given socket.
	If the expected message is not received, then the program terminates.
	By default, the message is "OK", but can be changed
	:param socket: Socket with which the connection has already been estabilished
	:param message: [Optional] The expected message through the socket
	'''
	if socket.recv(2048).decode('ascii') != message:
		print("ERROR: Acknowledgement not received")
		exit(1)

def sendAcknowledgment(socket, message="OK"):
	'''
	This function sends a message through the passed socket.
	By default, the message is "OK", but can be changed
	:param socket: Socket with which the connection has already been estabilished
	:param message: [Optional] The message to be sent to through the socket
	'''
	socket.send(message.encode('ascii'))

def getEncodingParameters(fogName, cameraName):
	with open("./encoding_videos/{}/{}/params.txt".format(fogName, cameraName), "r") as file:
		content = file.read().strip()
	return content
	# return "Parameters: Bitrate-100; FPS-10"
def receiveFiles(connectionSocket, folderName, listeningProcessPid, fogName, cameraName):
	'''
	The function receives video files from the given socket and saves those videos in
	the given folder name.
	:param connectionSocket: Socket with which the connection has already been established
	:param folderName: Folder name in which the videos have to be stored upon receival
	:param listeningProcessPid: The process id of the process listening to the video receiving
	'''
	#Setup handler
	signal.signal(signal.SIGUSR1, listeningProcessReceivedVideo)
	signal.signal(signal.SIGABRT, receiveEncodingParams)

	global receiveMoreVideos, sendEncodingParams

	count_files = 0  # Num of files received

	# Byte which denotes the calculation of encoding parameters
	encodingCalculationByte = "CALC".encode('ascii')

	# Byte which denotes the video termination
	videoTerminationByte = "END".encode('ascii')

	# A flag to denote that the server has to compute the encoding params
	calculateEncodingParams = False

	receivedAllVideos = False
	# Receiving the video file
	while not receivedAllVideos:
		fileName = "{}.mp4".format(str(count_files))
		videoReceived = bytes()  # Video initialization
		with open(os.path.join(folderName, fileName), 'wb') as file:
			# Receiving the video until the termination
			while True:
				recvfile = connectionSocket.recv(4096)
				videoReceived += recvfile  # Appending to the received video

				if recvfile.startswith(encodingCalculationByte):
					videoReceived = videoReceived[len(encodingCalculationByte):]
					calculateEncodingParams = True
					print("ENCODING CALCULATION REQUEST RECEIVED")

				# print(recvfile)
				if recvfile.endswith(videoTerminationByte):
					videoReceived = videoReceived[:-len(videoTerminationByte)]
					count_files += 1
					print("FILE RECEIVED")
					if sendEncodingParams:
						parameters = getEncodingParameters(fogName, cameraName)
						print("NICE"*10)
						sendAcknowledgment(connectionSocket, parameters)
						sendEncodingParams = False
					else:
						sendAcknowledgment(connectionSocket)
					break
				elif not recvfile:  # When client connection terminates
					receivedAllVideos = True
					os.remove(os.path.join(folderName, fileName))
					break
			# Writing to a file
			if not receivedAllVideos:
				file.write(videoReceived)

				# When encoding parameters have to be calculated, send its signal
				if calculateEncodingParams:
					print("SEND ENCODING SIGNAL TO CHILD")
					# Send a signal to denote that the
					os.kill(listeningProcessPid, signal.SIGUSR2)
					calculateEncodingParams = False
				# Otherwise, send the normal video receival signal
				else:
					os.kill(listeningProcessPid, signal.SIGUSR1)

				#Wait for the listening process to receive the video
				while True:
					if receiveMoreVideos:
						receiveMoreVideos = False
						break
					else:
						# print("========= BEFORRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
						signal.pause()
						# print("========= AFTRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")

	# Terminate the listening process
	os.kill(listeningProcessPid, signal.SIGINT)


def clientProcessFunctionality(connectionSocket):
	'''
	- Receives the information about the fog node and camera
	- Sets up a process to listen to the incoming files in the camera folder
	- Receive the files from the client
	:param connectionSocket: Socket with which the connection has already been estabilished
	'''
	signal.signal(signal.SIGUSR2, listeningProcessReady)

	# Getting Fog node name
	fogName = connectionSocket.recv(2048).decode('ascii')
	print("Fog name is:", fogName)
	sendAcknowledgment(connectionSocket)
	# Getting the camera name
	cameraName = connectionSocket.recv(2048).decode('ascii')
	print("Cam name is:", cameraName)
	sendAcknowledgment(connectionSocket)

	folderPath = "./streamed_files/{}/{}".format(fogName, cameraName)

	process = subprocess.Popen(["python3", "./vehicle_counting_algorithm/listenToStreamedFiles.py", "-fp", folderPath])

	# Waiting until the listening process is ready
	while True:
		signal.pause() #Suspends the current process
		if listening:
			break

	# Receive files from the socket and store them
	receiveFiles(connectionSocket, folderPath, process.pid, fogName, cameraName)

	print("Closing socket")
	connectionSocket.close()
