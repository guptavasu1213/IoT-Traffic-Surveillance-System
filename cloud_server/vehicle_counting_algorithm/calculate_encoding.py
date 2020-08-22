import os

#Error threshold for computing the optimal parameters
THRESHOLD = 0.10
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

def grid_search(video_path, high_resolution_count):
	#CALC THE ENCODING PARAMS BASED ON THE THRESHOLD AND THE EXISTING COUNT
	bitrate, fps = 500, 9
	# dummySleep(4)
	return bitrate, fps

def save_parameters(filepath, bitrate, fps):
	with open(filepath, 'w') as f:
		f.write("Parameters: Bitrate-{}; FPS-{}".format(bitrate, fps))

def calculate_encoding_params(path_to_folder, high_resolution_count):
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

	#Concatenating all files into one
	os.system("ffmpeg -f concat -safe 0 -i {} -c copy {} -y 2>/dev/null".format(temp_file_path, concat_output_file_path))

	#Grid search the optimal parameters
	bitrate, fps = grid_search(concat_output_file_path, high_resolution_count)

	#Save parameters in a log file
	save_parameters(parameter_log_file_path, bitrate, fps)

	os.remove(temp_file_path)