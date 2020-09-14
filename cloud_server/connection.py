import os
import signal
import subprocess

# Handler flags
listening = False
receive_more_videos = False
send_encoding_params = False

def listening_process_ready(signum, stack):
	'''
	Signal handler for SIGUSR2 to specify that the child process is ready to listen
	'''
	global listening
	listening = True

def listening_process_received_video(signum, stack):
	'''
	Signal handler for SIGUSR1 to specify that the child process has received the video
	'''
	global receive_more_videos
	receive_more_videos = True

def receive_encoding_params(signum, stack):
	'''
	Signal handler for SIGABRT to notify the sending of encoding parameters to the fog node
	'''
	global send_encoding_params
	send_encoding_params = True

def receive_acknowlegdement(socket, message="OK"):
	'''
	This function waits to receive a message at the given socket.
	If the expected message is not received, then the program terminates.
	By default, the message is "OK", but can be changed
	:param socket: Socket with which the connection has already been established
	:param message: [Optional] The expected message through the socket
	'''
	if socket.recv(2048).decode('ascii') != message:
		print("ERROR: Acknowledgement not received")
		exit(1)

def send_acknowledgment(socket, message="OK"):
	'''
	This function sends a message through the passed socket.
	By default, the message is "OK", but can be changed
	:param socket: Socket with which the connection has already been established
	:param message: [Optional] The message to be sent to through the socket
	'''
	socket.send(message.encode('ascii'))

def get_encoding_parameters(fog_name, camera_name):
	'''
	Retrieving the calculated encoding parameters for the given fog node and the camera
	:param fog_name: The name of fog node
	:param camera_name: The name of camera
	'''
	with open("./encoding_videos/{}/{}/params.txt".format(fog_name, camera_name), "r") as file:
		content = file.read().strip()
	return content

def receive_files(connection_socket, folder_name, listening_process_pid, fog_name, camera_name):
	'''
	The function receives video files from the given socket and saves those videos in
	the given folder name.
	:param connection_socket: Socket with which the connection has already been established
	:param folder_name: Folder name in which the videos have to be stored upon receival
	:param listening_process_pid: The process id of the process listening to the video receiving
	:param fog_name: The name of fog node
	:param camera_name: The name of camera
	'''
	#Setup handler
	signal.signal(signal.SIGUSR1, listening_process_received_video)
	signal.signal(signal.SIGABRT, receive_encoding_params)

	global receive_more_videos, send_encoding_params

	count_files = 0  # Num of files received

	# Byte which denotes the calculation of encoding parameters
	encoding_calculation_byte = "CALC".encode('ascii')

	# Byte which denotes the video termination
	video_termination_byte = "END".encode('ascii')

	# A flag to denote that the server has to compute the encoding params
	calculate_encoding_params = False

	received_all_videos = False
	# Receiving the video file
	while not received_all_videos:
		file_name = "{}.mp4".format(str(count_files))
		video_received = bytes()  # Video initialization
		with open(os.path.join(folder_name, file_name), 'wb') as file:
			# Receiving the video until the termination
			while True:
				recvfile = connection_socket.recv(4096)
				video_received += recvfile  # Appending to the received video

				if recvfile.startswith(encoding_calculation_byte):
					video_received = video_received[len(encoding_calculation_byte):]
					calculate_encoding_params = True

				if recvfile.endswith(video_termination_byte):
					video_received = video_received[:-len(video_termination_byte)]
					count_files += 1
					# If encoding parameters are calculated, send them to the fog node
					if send_encoding_params:
						parameters = get_encoding_parameters(fog_name, camera_name)
						send_acknowledgment(connection_socket, parameters)
						send_encoding_params = False
					#Else, send an "OK" acknowledgement
					else:
						send_acknowledgment(connection_socket)
					break
				elif not recvfile:  # When client connection terminates
					received_all_videos = True
					os.remove(os.path.join(folder_name, file_name))
					break
			# Writing to a file and notifying the listening process about the file receival
			if not received_all_videos:
				file.write(video_received)

				# When encoding parameters have to be calculated, send its signal
				if calculate_encoding_params:
					# Send a signal to denote that the
					os.kill(listening_process_pid, signal.SIGUSR2)
					calculate_encoding_params = False
				# Otherwise, send the normal video receival signal
				else:
					os.kill(listening_process_pid, signal.SIGUSR1)

				#Wait for the listening process to receive the video
				while True:
					if receive_more_videos:
						receive_more_videos = False
						break
					else:
						signal.pause()

	# Terminate the listening process
	os.kill(listening_process_pid, signal.SIGINT)

def check_camera_registration(folder_path):
	'''
	Check if the camera is registered by verifying the existence of the camera folder.
	:param folder_path: Path to the camera folder
	'''
	if not os.path.exists(folder_path):
		print("ERROR: The camera is not registered.")
		exit(1)

def is_registation_request(connection_socket):
	'''
	Check if the message sent by the fog node is for registering new devices
	The program registers the camera and exits if the registration message is received.
	:return : Fog node and camera name (if the program does not exit)
	'''
	message = connection_socket.recv(2048).decode('ascii')
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

def receive_and_analyze_videos(connection_socket, encoding_time):
	'''
	- Receives the information about the fog node and camera
	- Sets up a process to listen to the incoming files in the camera folder
	- Receive the files from the client
	:param connection_socket: Socket with which the connection has already been estabilished
	:param encoding_time: The duration of video analysis to calculate the encoding parameters 
	'''
	signal.signal(signal.SIGUSR2, listening_process_ready)

	fog_name, camera_name, duration = is_registation_request(connection_socket)
	send_acknowledgment(connection_socket)

	print("Fog name is:", fog_name)
	print("Cam name is:", camera_name)

	folder_path = "./streamed_files/{}/{}".format(fog_name, camera_name)

	# Check if the camera is registered
	check_camera_registration(folder_path)

	# Spawn a process to listen to the streamed files and perform analysis upon receival
	process = subprocess.Popen(["python3", "./traffic_density_measurement_algorithm/listenToStreamedFiles.py",
		"-fp", folder_path, "-d", duration, "-et", encoding_time])

	# Waiting until the listening process is ready
	while True:
		signal.pause() # Suspends the current process
		if listening:
			break

	# Receive files from the socket and store them
	receive_files(connection_socket, folder_path, process.pid, fog_name, camera_name)

	print("Closing socket")
	connection_socket.close()