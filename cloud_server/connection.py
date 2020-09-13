import os
import signal
import subprocess

# Handler flags
listening = False
receiveMoreVideos = False
sendEncodingParams = False

def listeningProcessReady(signum, stack):
	'''
	Signal handler for SIGUSR2 to specify that the child process is ready to listen
	'''
	global listening
	listening = True

def listeningProcessReceivedVideo(signum, stack):
	'''
	Signal handler for SIGUSR1 to specify that the child process has received the video
	'''
	global receiveMoreVideos
	receiveMoreVideos = True

def receiveEncodingParams(signum, stack):
	'''
	Signal handler for SIGABRT to notify the sending of encoding parameters to the fog node
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
	'''
	Retrieving the calculated encoding parameters for the given fog node and the camera
	:param cameraName: The name of camera
	:param fogNodeName: The name of fog node
	'''
	with open("./encoding_videos/{}/{}/params.txt".format(fogName, cameraName), "r") as file:
		content = file.read().strip()
	return content

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

				if recvfile.endswith(videoTerminationByte):
					videoReceived = videoReceived[:-len(videoTerminationByte)]
					count_files += 1
					print("FILE RECEIVED")
					# If encoding parameters are calculated, send them to the fog node
					if sendEncodingParams:
						parameters = getEncodingParameters(fogName, cameraName)
						sendAcknowledgment(connectionSocket, parameters)
						sendEncodingParams = False
					#Else, send an "OK" acknowledgement
					else:
						sendAcknowledgment(connectionSocket)
					break
				elif not recvfile:  # When client connection terminates
					receivedAllVideos = True
					os.remove(os.path.join(folderName, fileName))
					break
			# Writing to a file and notifying the listening process about the file receival
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
						signal.pause()
						print("========= AFTRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")

	# Terminate the listening process
	os.kill(listeningProcessPid, signal.SIGINT)

def check_camera_registration(folder_path):
	'''
	Check if the camera is registered by verifying the existence of the camera folder.
	:param folder_path: Path to the camera folder
	'''
	if not os.path.exists(folder_path):
		print("ERROR: The camera is not registered.")
		exit(1)

def is_registation_request(connectionSocket):
	'''
	Check if the message sent by the fog node is for registering new devices
	The program registers the camera and exits if the registration message is received.
	:return : Fog node and camera name (if the program does not exit)
	'''
	message = connectionSocket.recv(2048).decode('ascii')
	splitted_message = message.split("~")
	if message.startswith("REGISTER CAM"):
		print("Camera Registration Message received!")
		fog_name = splitted_message[1]
		cam_name = splitted_message[2]
		line_coordinates = splitted_message[3]

		# Register Cam and its corresponding line coordinates
		from register_camera import register
		register(fog_name, cam_name, line_coordinates)
		exit(0)
	return splitted_message

def receiveAndAnalyzeVideos(connectionSocket):
	'''
	- Receives the information about the fog node and camera
	- Sets up a process to listen to the incoming files in the camera folder
	- Receive the files from the client
	:param connectionSocket: Socket with which the connection has already been estabilished
	'''
	signal.signal(signal.SIGUSR2, listeningProcessReady)

	fog_name, camera_name = is_registation_request(connectionSocket)
	sendAcknowledgment(connectionSocket)

	print("Fog name is:", fog_name)
	print("Cam name is:", camera_name)

	folder_path = "./streamed_files/{}/{}".format(fog_name, camera_name)

	# Check if the camera is registered
	check_camera_registration(folder_path)

	# Spawn a process to listen to the streamed files and perform analysis upon receival
	process = subprocess.Popen(["python3", "./vehicle_counting_algorithm/listenToStreamedFiles.py", "-fp", folder_path])

	# Waiting until the listening process is ready
	while True:
		signal.pause() # Suspends the current process
		if listening:
			break

	# Receive files from the socket and store them
	receiveFiles(connectionSocket, folder_path, process.pid, fog_name, camera_name)

	print("Closing socket")
	connectionSocket.close()
receiveAndAnalyzeVideos