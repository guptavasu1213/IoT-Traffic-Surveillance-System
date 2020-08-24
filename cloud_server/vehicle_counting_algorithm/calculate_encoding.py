import os

#Error threshold for computing the optimal parameters
THRESHOLD = 0.20
#####################REMOVE THIS FROM HERE
import time
def dummySleep(max_time):
	st = time.time()
	while time.time() - st < max_time:  # Goes through the loop for the specified time
		continue

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

def grid_search(video_path, path_to_folder, high_resolution_count, count_vehicles, initialize_vars,
				line_coordinates, currentResolution):
	#CALC THE ENCODING PARAMS BASED ON THE THRESHOLD AND THE EXISTING COUNT
	bitrate, fps = 100, 7
	encoding_counter = 1 # Number of times encoding has happened
	BITRATE_STEP, FPS_STEP = 50, 2
	NUM_VIDEOS_TO_SKIP = 4

	temp_output_file = os.path.join(path_to_folder, "temp.mp4")

	while True:
		#Convert the video to this encoding
		os.system("ffmpeg -i {} -r {} -b:v {}k -an -y {} 2>/dev/null".format(video_path, fps, bitrate, temp_output_file))

		#Initialize the detection
		initialize_vars(line_coordinates, currentResolution)
		#Run the detection with this file
		vehicle_count = count_vehicles(temp_output_file)
		print("\n\n==========> MY COUNT:", vehicle_count, "HIGH RES:", high_resolution_count)
		# If the error is within the threshold, then break
		detection_error = abs(high_resolution_count - vehicle_count) / high_resolution_count
		print(detection_error, THRESHOLD)
		if (detection_error <= THRESHOLD):
			break
		else:
			if encoding_counter % NUM_VIDEOS_TO_SKIP != 0: # Skipping every nth video
				print("INCREMENT BR")
				bitrate += BITRATE_STEP #Incrementing the bitrate
			else:
				print("INCREMENT FPS")
				fps += FPS_STEP #Incrementing the FPS
			encoding_counter += 1

	# os.remove(temp_output_file)
	return bitrate, fps

def save_parameters(filepath, bitrate, fps):
	with open(filepath, 'w') as f:
		f.write("Parameters: Bitrate-{}; FPS-{}".format(bitrate, fps))

def calculate_encoding_params(path_to_folder, high_resolution_count, count_vehicles, initialize_vars,
							  line_coordinates, currentResolution):
	'''
	Compute the encoding parameters and save them in a text file
	'''
	fPath = os.path.join(path_to_folder, "videos")
	temp_file_path = os.path.join(path_to_folder, "file_names.txt")
	concat_output_file_path = os.path.join(path_to_folder, "videos", "output.mp4")
	parameter_log_file_path = os.path.join(path_to_folder, "params.txt")

	str_to_write = ""
	for file in sortFiles(os.listdir(fPath)):
		str_to_write += "file " + os.path.join(fPath, file) + "\n"

	with open(temp_file_path, 'w') as f:
		f.write(str_to_write)

	print("Concatenating files:", str_to_write)
	#Concatenating all files into one
	os.system("ffmpeg -f concat -safe 0 -i {} -c copy {} -y 2>/dev/null".format(temp_file_path, concat_output_file_path))

	#Grid search the optimal parameters
	bitrate, fps = grid_search(concat_output_file_path, path_to_folder, high_resolution_count,
							   count_vehicles, initialize_vars, line_coordinates, currentResolution)

	#Save parameters in a log file
	save_parameters(parameter_log_file_path, bitrate, fps)

	os.remove(temp_file_path)
	# os.remove(concat_output_file_path)
	os.system("rm {}/*.mp4".format(fPath))