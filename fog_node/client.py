import socket
import sys
import os
import time
from encoding import encode_video, get_video_length

def receiveAcknowlegdement(socket, message="OK", expectEncodingParams=False):
	'''
	This function waits to receive a message at the given socket.
	If the expected message is not received, then the program terminates.
	By default, the message is "OK", but can be changed

	:param socket: Socket with which the connection has already been estabilished
	:param message: [Optional] The expected message through the socket
	:param expectEncodingParams: [Optional]	Expecting encoding parameters in the message

	:return: Encoding parameters if the encoding parameters are found in the message when
	the expectEncodingParams flag is True
	'''
	socket_message = socket.recv(2048).decode('ascii')
	if expectEncodingParams:
		if socket_message.startswith("Parameters:"):
			return socket_message
	if socket_message != message:
		print("ERROR: Acknowledgement not received")
		exit(1)

def sendAcknowledgment(socket, message="OK"):
	'''
	This function sends a message through the passed socket.
	By default, the message is "OK", but can be changed
	'''
	socket.send(message.encode('ascii'))

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

def client(fogNodeName, cameraName, server_IP, server_port, max_encoding_calc_time):
	'''
	Initiates the client and attempts to build a connection with the server
	:param fogNodeName:
	++++++++++++++++++++++
	++++++++++++++++++++++
	:param max_encoding_calc_time: The time interval at which the high resolution video with is sent for calculating the encoding
	'''

	#Create client socket that using IPv4 and TCP protocols
	try:
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as e:
		print('Error in client socket creation:',e)
		sys.exit(1)

	try:
		#Client connect with the server
		clientSocket.connect((server_IP, server_port))


		folderPath = "./surveillance-cam-videos/" + cameraName
		videoFiles = sortFiles(os.listdir(folderPath))

		video_length = get_video_length(os.path.join(folderPath, videoFiles[0]))

		#Send Fog Node name and Camera name
		clientSocket.send("{}~{}~{}".format(fogNodeName, cameraName, str(video_length)).encode('ascii'))
		receiveAcknowlegdement(clientSocket)

		# Byte which denotes the calculation of encoding parameters
		encodingCalculationByte = "CALC".encode('ascii')

		#Byte which denotes the video termination
		terminationByte = "END".encode('ascii')

		startEncodingCalculationTime = 0
		videoLen = 1 # Length of each video in secs

		encoding_params = None

		for fileName in videoFiles:
			time.sleep(videoLen) #To simulate the recording in real-time

			filePath = os.path.join(folderPath, fileName)

			#Checking if the high resolution video for encoding should be sent or not
			if startEncodingCalculationTime % max_encoding_calc_time == 0:
				sendFile = encodingCalculationByte
				encoding_params = None #Seng high quality video now
				print("Send high res")
			else:
				sendFile = bytes()

			if encoding_params is not None:
				print("ENCODING:", fileName)
				filePath = encode_video(filePath, encoding_params, fogNodeName, cameraName)

			with open(filePath, 'rb') as file:
				sendFile += file.read()

			#Appending termination byte at the end of the video
			sendFile += terminationByte
			clientSocket.sendall(sendFile) #Send the entire video
			# Waiting for server acknowledgment for the full video receival
			response = receiveAcknowlegdement(clientSocket, expectEncodingParams=True)
			if response is not None: # When encoding params are received
				print("GOT PARAMS", response)
				encoding_params = response
			print("{} : {} -- Video sent".format(cameraName, fileName))

			startEncodingCalculationTime += videoLen
		# Client terminate connection with the server
		clientSocket.close()

	except socket.error as e:
		print('An error occurred:',e)
		clientSocket.close()
		sys.exit(1)
