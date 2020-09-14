import os

#Error threshold for computing the optimal parameters
THRESHOLD = 0.20

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

def grid_search(video_path, path_to_folder, high_resolution_count, count_vehicles, initialize_vars,
				line_coordinates, current_resolution):
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
		initialize_vars(line_coordinates, current_resolution)
		#Run the detection with this file
		vehicle_count = count_vehicles(temp_output_file)
		print("\n\nCount with given encoding: {}\tHIGH RES: {}".format(vehicle_count, high_resolution_count))
		# If the error is within the threshold, then break
		detection_error = abs(high_resolution_count - vehicle_count) / high_resolution_count
		print(detection_error, THRESHOLD)
		if (detection_error <= THRESHOLD):
			break
		else:
			if encoding_counter % NUM_VIDEOS_TO_SKIP != 0: # Skipping every nth video
				print("INCREMENT BR to", bitrate)
				bitrate += BITRATE_STEP #Incrementing the bitrate
			else:
				print("INCREMENT FPS to", fps)
				fps += FPS_STEP #Incrementing the FPS
			encoding_counter += 1

	os.remove(temp_output_file)
	return bitrate, fps

def save_parameters(file_path, bitrate, fps):
	'''
	:param file_path: The path of the file in which the parameters have to be written
 	:param bitrate: Bitrate
	:param fps: Frames per second (fps)
	'''
	with open(file_path, 'w') as f:
		f.write("Parameters: Bitrate-{}; FPS-{}".format(bitrate, fps))

def calculate_encoding_params(path_to_folder, high_resolution_count, count_vehicles, initialize_vars,
							  line_coordinates, current_resolution):
	'''
	Compute the encoding parameters and save them in a text file
	:param path_to_folder: Path to the encoding folder
	:param high_resolution_count: The count of the high resolution video
	:param count_vehicles: Function for counting vehicles
	:param initialize_vars: Function for initializing variables in the vehicle counting algorithm
	:param line_coordinates: The line coordinates for the camera used for counting
	:param current_resolution: The resolution of the video
	'''
	f_path = os.path.join(path_to_folder, "videos")
	temp_file_path = os.path.join(path_to_folder, "file_names.txt")
	concat_output_file_path = os.path.join(path_to_folder, "videos", "output.mp4")
	parameter_log_file_path = os.path.join(path_to_folder, "params.txt")

	str_to_write = ""
	for file in sort_files(os.listdir(f_path)):
		str_to_write += "file " + os.path.join(f_path, file) + "\n"

	with open(temp_file_path, 'w') as f:
		f.write(str_to_write)

	print("Concatenating files:", str_to_write)
	#Concatenating all files into one
	os.system("ffmpeg -f concat -safe 0 -i {} -c copy {} -y 2>/dev/null".format(temp_file_path, concat_output_file_path))

	#Grid search the optimal parameters
	bitrate, fps = grid_search(concat_output_file_path, path_to_folder, high_resolution_count,
							   count_vehicles, initialize_vars, line_coordinates, current_resolution)

	#Save parameters in a log file
	save_parameters(parameter_log_file_path, bitrate, fps)

	# Removing all the temporary files
	os.remove(temp_file_path)
	os.system("rm {}/*.mp4".format(f_path))