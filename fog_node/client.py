import socket
import sys
import os
import time

def receiveAcknowlegdement(socket, message="OK"):
	'''
	This function waits to receive a message at the given socket.
	If the expected message is not received, then the program terminates.
	By default, the message is "OK", but can be changed
	'''
	if socket.recv(2048).decode('ascii') != message:
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

def client(fogNodeName, cameraName):
	'''
	Initiates the client and attempts to build a connection with the server
	'''
	# Server Information
	serverName = '199.116.235.176'
	serverPort = 12000

	#Create client socket that using IPv4 and TCP protocols
	try:
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as e:
		print('Error in client socket creation:',e)
		sys.exit(1)

	try:
		#Client connect with the server
		clientSocket.connect((serverName,serverPort))

		#Send Fog Node Name
		clientSocket.send(fogNodeName.encode('ascii'))
		receiveAcknowlegdement(clientSocket)

		# Send Camera name
		clientSocket.send(cameraName.encode('ascii'))
		receiveAcknowlegdement(clientSocket)

		folderPath = "./street-cam-videos/" + cameraName
		videoFiles = sortFiles(os.listdir(folderPath))

		#Byte which denotes the video termination
		terminationByte = "END".encode('ascii')

		for fileName in videoFiles:
			# count = 0
			filePath = os.path.join(folderPath, fileName)
			# filename = "/home/vasu/Documents/street-videos/youtubeDownloads/easy.mp4"
			with open(filePath, 'rb') as file:
				sendfile = file.read()
				'''
				==== If sending a file in pieces
				while True:
					count += 1
					sendfile = file.read(4096)
					if not sendfile: break
					# print(count)
					clientSocket.send(sendfile)
				'''
			#Appending termination byte at the end of the video
			sendfile += terminationByte
			clientSocket.sendall(sendfile) #Send the entire video
			# Waiting for server acknowlegment for the full video receival
			receiveAcknowlegdement(clientSocket)
			print("{} : {} -- Video sent".format(cameraName, fileName))

		# Client terminate connection with the server
		clientSocket.close()

	except socket.error as e:
		print('An error occured:',e)
		clientSocket.close()
		sys.exit(1)

#----------
# client()
