'''
This file listens to the videos received by the server by the fog node and analyze the received videos.
'''
import argparse
import os

ap = argparse.ArgumentParser()
ap.add_argument("-fp", "--folder_path", help="folder path of streamed camera videos", required=True)
ap.add_argument("-d", "--duration", help="duration of each video segment", required=True, type=float)
ap.add_argument("-et", "--encoding_time", help="The duration of video analysis to calculate the encoding parameters",
				required=True, type=int)
args = vars(ap.parse_args())

# Error check the folder path
folder_path = args["folder_path"].strip()

if not os.path.isdir(folder_path):
	print("ERROR: The specified folder path is invalid")
	exit(1)

import signal

from main_live_stream import *
from calculate_encoding import calculate_encoding_params

# Flags for handlers
num_videos_received = 0
terminate = False
ppid = 0
video_num_to_start_encoding = None

VIDEO_LENGTH = args["duration"] #SEC
ENCODING_COMPUTATION_TIME = args["encoding_time"] #Num of secs the encoding should be performed for
NUM_VIDEOS_FOR_ENCODING = round(ENCODING_COMPUTATION_TIME/VIDEO_LENGTH)

def process_videos(signum, stack):
	'''
	Signal handler for SIGUSR1 for receiving a signal to process video files
	'''
	global num_videos_received
	num_videos_received += 1
	os.kill(ppid, signal.SIGUSR1)

def signal_encode_params(signum, stack):
	'''
	Signal handler for SIGUSR2 to start video encoding
	'''
	global video_num_to_start_encoding, num_videos_received
	num_videos_received += 1
	video_num_to_start_encoding = num_videos_received
	os.kill(ppid, signal.SIGUSR1)

def terminate_process(signum, stack):
	'''
	Signal handler for SIGINT for the termination of the current process
	'''
	# If video analysis is ongoing, then set the terminate flag to True
	if num_videos_received > 0:
		global terminate
		terminate = True
	else:  # Terminating when there is no ongoing video analysis
		exit(0)

def get_fog_and_camera_name(folder_path):
	'''
	Extracting the fog node name and the camera name from the file path
	:param videoFilePath: Path to the video file
	:return: Camera name, Fog Node name
	'''
	folder_path += "/"
	splitted_path = folder_path.split("/")
	if splitted_path[-1] == "":
		return splitted_path[-2], splitted_path[-3]
	else:
		return splitted_path[-1], splitted_path[-2]

def get_line_coordinates_file_name():
	'''
	Retrieving the line coordinates for the camera based on the folder path of the video stream
	'''
	last_slash_index = folder_path.rfind("/")
	if last_slash_index == len(folder_path)-1:
		last_slash_index = folder_path[:-1].rfind("/")
	return folder_path[:last_slash_index + 1] + "line_coordinates.txt"

def get_count_log_file_path(camera_name, fog_node_name):
	'''
	Retrieving the count log file path for the camera based on the folder path of the video stream
	:param camera_name: The name of camera
	:param fog_node_name: The name of fog node
	'''
	index = folder_path.find("streamed_files")
	return os.path.join(folder_path[:index], "detection_logs", fog_node_name, camera_name, "log.txt")

def get_encoded_video_folder_path(camera_name, fog_node_name):
	'''
	Retrieving the path of the folder containing encoded videos for the given camera and fog node
	:param camera_name: The name of camera
	:param fog_node_name: The name of fog node
	'''
	index = folder_path.find("streamed_files")
	return os.path.join(folder_path[:index], "encoding_videos", fog_node_name, camera_name)

def get_line_coordinates_for_camera(camera_name):
	'''
	Extracts the line(s) coordinates for the given fog node and the camera
	fileName: The file name of the video
	:param camera_name: The name of camera
	'''
	#Open line coordinates file
	with open(get_line_coordinates_file_name()) as file:
		coordinates_file = file.read()

	camera_index = coordinates_file.find(camera_name)
	newline_index = coordinates_file.find('\n', camera_index)

	if camera_index == -1:
		print("ERROR: Line coordinates not found")
		os.kill(ppid, signal.SIGTERM) #Terminate the listening parent process
		exit(0)

	line_in_file = coordinates_file[camera_index:newline_index]
	lines = line_in_file[line_in_file.find(':')+1:]
	return lines

def sort_files(file_list):
	'''
	The list of files is sorted and returned back
	:param file_list: List of file names which are of the form "<integer>.<extension>"
	:return: A list of sorted files
	'''
	sorted_files_without_extension = dict()
	for file in file_list:
		try:
			sorted_files_without_extension[(int(file.split(".")[0]))] = file
		except:
			print("\n\nERROR: The file name should only contain a number with an extension."
				  "Example: 1.mp4")
	sorted_files = []
	for file in sorted(sorted_files_without_extension):
		sorted_files.append(sorted_files_without_extension[file])
	return sorted_files

def get_video_resolution(video_path):
	'''
	Getting the resolution of the video
	:param video_path: The path of the video whose resolution has to be calculated
	:return: A list containing: [<width>, <height>]
	'''
	import tempfile
	import re

	tmpf = tempfile.NamedTemporaryFile()
	os.system("ffmpeg -i \"%s\" 2> %s" % (video_path, tmpf.name))
	lines = tmpf.readlines()
	tmpf.close()
	for line in lines:
		line = line.decode('UTF-8').strip()
		if line.startswith('Stream #0:0'):
			resolution = re.search('([1-9]\d+x\d+)', line).group(1)
			return [int(val) for val in resolution.strip().split('x')]

def main_listen():
	'''
	To listen to the folder with received files, this process communicates with the parent
	process and receives signal from it whenever
    '''
	global ppid, folder_path, num_videos_received, video_num_to_start_encoding
	ppid = os.getppid()
	num_videos_analyzed = 0
	resolution = None

	folder_path = os.path.abspath(folder_path)
	camera_name, fog_node_name = get_fog_and_camera_name(folder_path)
	count_file_path = get_count_log_file_path(camera_name, fog_node_name)
	encoding_folder_path = get_encoded_video_folder_path(camera_name, fog_node_name)
	line_coordinates = get_line_coordinates_for_camera(camera_name)

	# Setup signal handlers
	signal.signal(signal.SIGUSR1, process_videos)
	signal.signal(signal.SIGUSR2, signal_encode_params)
	signal.signal(signal.SIGINT, terminate_process)

	sorted_files = []

	# Send a ready signal to the parent process
	os.kill(ppid, signal.SIGUSR2)
	while True:
		signal.pause()

		# Loop runs until the all the videos received have been analyzed
		while num_videos_analyzed < num_videos_received:
			if sorted_files == []: # Creating a list of files in sorted order
				video_files = os.listdir(folder_path)
				sorted_files = sort_files(video_files)

			video_file = sorted_files.pop(0) #Retreive the next file to analyze
			print("Analyzing file: ", video_file)
			video_abs_path = os.path.abspath(os.path.join(folder_path, video_file))
			start_vid_num = video_num_to_start_encoding #Global variable can change, so create a local copy

			# If the video is the first to be encoded
			if num_videos_analyzed+1 == start_vid_num:
				# Storing the counts before initializing the framework
				write_count(count_file_path)

				print("\n\nXXXXXXXXXXXXXXXXXXXX CALCULATE ENCODING NOW with FIRST", video_file, "XXXXXXXXXXXXXXXXXXXX")

				# Initializing the framework
				resolution = get_video_resolution(video_abs_path)
				initialize_vars(line_coordinates, resolution)

				#Removes all files in the encoding folder (if any)
				f_path = os.path.join(encoding_folder_path, "videos")
				if len(os.listdir(f_path)):
					os.system("rm {}/*.mp4".format(f_path))

			# Perform vehicle counting
			count_vehicles(video_abs_path)

			if 	num_videos_analyzed+1 >= start_vid_num and \
				num_videos_analyzed+1 <=  start_vid_num + NUM_VIDEOS_FOR_ENCODING-1:

				# Move the video to the encoding folder
				os.rename(video_abs_path, os.path.join(encoding_folder_path, "videos", video_file))

				if num_videos_analyzed+1 ==  start_vid_num + NUM_VIDEOS_FOR_ENCODING-1:
					# if at the last video, compute the encoding parameters
					high_resolution_count = get_vehicle_count()
					# Saving all the tracking components for the vehicle counting
					save_tracking_components()
					calculate_encoding_params(encoding_folder_path, high_resolution_count, count_vehicles,
											  initialize_vars, line_coordinates, resolution)
					# Restoring all the tracking components for the vehicle counting
					reload_from_saved()
					# Signalling the parent to notify the calculation of encoding parameters
					os.kill(ppid, signal.SIGABRT)
			else:
				#Removing file after analysis
				os.remove(video_abs_path)
			num_videos_analyzed += 1

		if terminate:
			print("=x" * 8, "Terminating analysis now", "=x" * 8)
			exit(0)
main_listen()