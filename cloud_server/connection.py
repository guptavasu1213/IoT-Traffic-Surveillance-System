from listenToStreamedFiles import *

#Handler flags
listening = False

def listeningProcessReady(signum, stack):
	'''
	Signal handler to specify that the child process is ready to listen
	'''
	global listening
	listening = True

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


def receiveFiles(connectionSocket, folderName, listeningProcessPid):
	'''
	The function receives video files from the given socket and saves those videos in
	the given folder name.
	:param connectionSocket: Socket with which the connection has already been estabilished
	:param folderName: Folder name in which the videos have to be stored upon receival
	:param listeningProcessPid: The process id of the process listening to the video receiving
	'''
	count_files = 0  # Num of files received
	# Byte which denotes the video termination
	videoTerminationByte = "END".encode('ascii')

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

				# print(recvfile)
				if recvfile.endswith(videoTerminationByte):
					videoReceived = videoReceived[:-len(videoTerminationByte)]
					count_files += 1
					print("FILE RECEIVED")
					os.kill(listeningProcessPid, signal.SIGUSR1)
					# Inform client about full video receival
					sendAcknowledgment(connectionSocket)
					break
				elif not recvfile:  # When client connection terminates
					receivedAllVideos = True
					os.remove(os.path.join(folderName, fileName))
					break
			# Writing to a file
			if not receivedAllVideos:
				file.write(videoReceived)
	# Terminate the listening process
	os.kill(listeningProcessPid, signal.SIGINT)


def clientProcessFunctionality(connectionSocket):
	'''
	- Receives the information about the fog node and camera
	- Sets up a process to listen to the incoming files in the camera folder
	- Receive the files from the client
	:param connectionSocket: Socket with which the connection has already been estabilished
	'''
	#Setup handler
	signal.signal(signal.SIGUSR2, listeningProcessReady)

	# Getting Fog node name
	fogName = connectionSocket.recv(2048).decode('ascii')
	print("Fog name is:", fogName)
	sendAcknowledgment(connectionSocket)
	# Getting the camera name
	cameraName = connectionSocket.recv(2048).decode('ascii')
	print("Cam name is:", cameraName)
	sendAcknowledgment(connectionSocket)

	folderName = "./streamed_files/{}/{}".format(fogName, cameraName)

	pid = os.fork()
	if pid == -1: #Fork failed
		exit(1)
	# Initiating a process for checking the files in the given folder
	elif pid == 0:
		listenToReceivedFiles(folderName)
		return

	# Waiting until the listening process is ready
	while True:
		signal.pause() #Suspends the current process
		if listening:
			break

	# Receive files from the socket and store them
	receiveFiles(connectionSocket, folderName, pid)

	print("Closing socket")
	connectionSocket.close()
