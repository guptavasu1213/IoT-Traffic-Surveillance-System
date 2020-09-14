import socket
import sys
import os
import time
from encoding import encode_video, get_video_length

def receive_acknowlegdement(socket, message="OK", expect_encoding_params=False):
	'''
	This function waits to receive a message at the given socket.
	If the expected message is not received, then the program terminates.
	By default, the message is "OK", but can be changed

	:param socket: Socket with which the connection has already been estabilished
	:param message: [Optional] The expected message through the socket
	:param expect_encoding_params: [Optional]	Expecting encoding parameters in the message

	:return: Encoding parameters if the encoding parameters are found in the message when
	the expectEncodingParams flag is True
	'''
	socket_message = socket.recv(2048).decode('ascii')
	if expect_encoding_params:
		if socket_message.startswith("Parameters:"):
			return socket_message
	if socket_message != message:
		print("ERROR: Acknowledgement not received")
		exit(1)

def send_acknowledgment(socket, message="OK"):
	'''
	This function sends a message through the passed socket.
	By default, the message is "OK", but can be changed
	'''
	socket.send(message.encode('ascii'))

def sort_files(file_list):
	'''
	:param file_list: List of file names which are of the form "<integer>.<extension>"
	'''
	sorted_files_without_extension = dict()
	for file in file_list:
		sorted_files_without_extension[(int(file.split(".")[0]))] = file

	sorted_files = []
	for file in sorted(sorted_files_without_extension):
		sorted_files.append(sorted_files_without_extension[file])
	return sorted_files

def client(fog_node_name, camera_name, server_ip, server_port, max_encoding_calc_time):
	'''
	Initiates the client and attempts to build a connection with the server
	:param fog_node_name: Fog node name
	:param camera_name: Camera Name
	:param server_ip: IP address of the server to connect with
	:param server_port: Port number of the server to connect with
	:param max_encoding_calc_time: The time interval at which the high resolution video with is sent for
	calculating the encoding (in seconds)
	'''

	# Create client socket that using IPv4 and TCP protocols
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as e:
		print('Error in client socket creation:',e)
		sys.exit(1)

	try:
		# Client connect with the server
		client_socket.connect((server_ip, server_port))

		folder_path = "./surveillance-cam-videos/" + camera_name
		video_files = sort_files(os.listdir(folder_path))

		# Get length of the first video to stream (in sec)
		video_length = get_video_length(os.path.join(folder_path, video_files[0]))

		# Send Fog Node name and Camera name
		client_socket.send("{}~{}~{}".format(fog_node_name, camera_name, str(video_length)).encode('ascii'))
		receive_acknowlegdement(client_socket)

		# Byte which denotes the calculation of encoding parameters
		encoding_calculation_byte = "CALC".encode('ascii')

		# Byte which denotes the video termination
		termination_byte = "END".encode('ascii')

		start_encoding_calculation_time = 0
		encoding_params = None

		for file_name in video_files:
			time.sleep(video_length) #To simulate the recording in real-time

			file_path = os.path.join(folder_path, file_name)

			# Checking if the high resolution video for encoding should be sent or not
			if start_encoding_calculation_time % max_encoding_calc_time == 0:
				send_file = encoding_calculation_byte
				encoding_params = None #Seng high quality video now
				print("Send high res")
			else:
				send_file = bytes()

			if encoding_params is not None:
				print("ENCODING:", file_name)
				file_path = encode_video(file_path, encoding_params, fog_node_name, camera_name)

			with open(file_path, 'rb') as file:
				send_file += file.read()

			#Appending termination byte at the end of the video
			send_file += termination_byte
			client_socket.sendall(send_file) #Send the entire video
			# Waiting for server acknowledgment for the full video receival
			response = receive_acknowlegdement(client_socket, expect_encoding_params=True)
			if response is not None: # When encoding params are received
				print("GOT PARAMS", response)
				encoding_params = response
			print("{} : {} -- Video sent".format(camera_name, file_name))

			start_encoding_calculation_time += video_length
		# Client terminate connection with the server
		client_socket.close()

	except socket.error as e:
		print('An error occurred:',e)
		client_socket.close()
		sys.exit(1)
