import os

import tempfile
import re

from encoding import *

THRESHOLD = 0.10 #Up to 10% error allowed

line_coordinates_filepath = "../streamed_files/coordinates.txt"

def getVideoDetails(filepath):
	'''
	Extracting the video encoding information like Duration, bit rate, codec,
	resolution, fps etc.
	'''
	tmpf = tempfile.NamedTemporaryFile()
	os.system("ffmpeg -i \"%s\" 2> %s" % (filepath, tmpf.name))
	lines = tmpf.readlines()
	tmpf.close()
	metadata = {}
	for l in lines:
		l = l.decode('UTF-8').strip()
		if l.startswith('Duration'):
			metadata['duration'] = re.search('Duration: (.*?),', l).group(0).split(':',1)[1].strip(' ,')
		if l.startswith('Stream #0:0'):
			metadata['codec'], metadata['profile'] = \
				[e.strip(' ,()') for e in re.search('Video: (.*? \(.*?\)),? ', l).group(0).split(':')[1].split('(')]
			metadata['resolution'] = re.search('([1-9]\d+x\d+)', l).group(1)
			br = re.search('(\d+ kb/s)', l).group(1)
			metadata['bitrate'] = br.split()[0]
			fps = re.search('(\d+ fps)', l).group(1)
			metadata['fps'] = fps.split()[0]
	return metadata

def getFileResolution(file_path):
	'''
	Resolution string is formatted like 'WxH' and this function seperates the 
	W and H as an integer and returns it back as an int array
	'''
	resolution = getVideoDetails(file_path)['resolution']
	return [int(val) for val in resolution.strip().split('x')]

def getLineCoordinates(fileName):
	'''
	Extracts the line(s) coordinates for the given video files
	fileName: The file name of the video
	'''
	#Open line coordinates file
	with open(line_coordinates_filepath) as file:
		coordinatesFile = file.read()

	fileNameIndex = coordinatesFile.find(fileName)
	newlineIndex = coordinatesFile.find('\n', fileNameIndex)

	if fileNameIndex == -1:
		print("No line_coordinates found")
		return False

	lineInFile = coordinatesFile[fileNameIndex:newlineIndex]
	lines = lineInFile[lineInFile.find(':')+1:]
	return lines

def get_file_name_from_path(file_path):
	'''
	Returns the file name without extension from the path
	'''
	return file_path[: file_path.rindex('.')].split("/")[-1] #without extension

def get_ext_from_path(file_path):
	'''
	Returns the extension of the file
	'''
	return file_path[file_path.rindex('.')+1 :]

def compute_vehicle_count(file_path, line_coordinates, resolutionRatio='1x1'):
	'''
	Computes the vehicle count for the given file name and returns the count
	'''
	count_file_name = os.path.abspath('count_logs/' + get_file_name_from_path(file_path) + ".txt")

	file_path = os.path.abspath(file_path)

	os.chdir('../vehicle_counting_algorithm')

	cmd = "python3 main.py -i " + file_path + " -lc \"" + \
		str(line_coordinates) + "\"" + " -r \"" + resolutionRatio +  "\" -cf " + count_file_name		
	print("Running command:\n" + cmd)
	subprocess.run(cmd, shell=True)
	os.chdir('../video_encoding')

	with open(count_file_name, 'r') as file:
		count = int(file.read().strip())
	return count

def calculate_bitrate(file_path, line_coordinates, vehicle_count_high_res):
	'''
	Calculate the lowest bitrate while having the detection loss within the threshold
	'''
	file_name, extension = get_file_name_from_path(file_path), get_ext_from_path(file_path)

	bitrate = 100 #kbps
	step = 50 #kbps
	
	#LOOP
	while True:
		#Convert the video to given bitrate
		new_file_path = "encoded_videos/" + file_name +'-bitrate-'+str(bitrate)+ "." + extension
		set_bitrate(file_path, new_file_path, bitrate)

		#Calculate the vehicle count on the low encoding video
		vehicle_count_low_res = compute_vehicle_count(new_file_path, line_coordinates)

		os.remove(new_file_path)
		#If the error is within the threshold, then break
		detection_error = abs(vehicle_count_high_res-vehicle_count_low_res)/vehicle_count_high_res
		print(detection_error, THRESHOLD)
		if (detection_error <= THRESHOLD):
			return bitrate
		#If the count is outside the threshold, then increase the bit rate
		else:
			bitrate = bitrate+step

def calculate_resolution(file_path, line_coordinates, vehicle_count_high_res):
	'''
	Calculate the lowest resolution while having the detection loss within the threshold
	'''
	originalResolution = getFileResolution(file_path)

	file_name, extension = get_file_name_from_path(file_path), get_ext_from_path(file_path)

	resolutionWidth = 200 
	step = 75

	#LOOP
	while True:
		#Convert the video to given resolution while maintaining the aspect ratio
		new_file_path = "encoded_videos/" + file_name +'-resolutionWidth-'+str(resolutionWidth)+ "." + extension

		#When conversion is unsuccessful        
		if not set_resolution(file_path, new_file_path, resolutionWidth,):
			# When an issue occurs while retrieving the video codec information, 
			# it means that the video conversion as not successful with the given resolution
			resolutionWidth += 1
			os.remove(new_file_path)
			continue

		decreasedResolution = getFileResolution(new_file_path)
		resolutionRatio = str(decreasedResolution[0]/originalResolution[0])+'x'+str(decreasedResolution[1]/originalResolution[1])

		#Calculate the vehicle count on the low encoding video
		vehicle_count_low_res = compute_vehicle_count(new_file_path, line_coordinates, resolutionRatio)

		os.remove(new_file_path)

		#If the error is within the threshold, then break
		detection_error = abs(vehicle_count_high_res-vehicle_count_low_res)/vehicle_count_high_res
		print(detection_error, THRESHOLD)
		if (detection_error <= THRESHOLD):
			return resolutionWidth
		#If the count is outside the threshold, then increase the resolution
		else:
			resolutionWidth = resolutionWidth+step

def calculate_fps(file_path, line_coordinates, vehicle_count_high_res):
	'''
	Calculate the lowest fps while having the detection loss within the threshold
	'''
	file_name, extension = get_file_name_from_path(file_path), get_ext_from_path(file_path)

	fps = 7 
	step = 3
	
	#LOOP
	while True:
		#Convert the video to given fps
		new_file_path = "encoded_videos/" + file_name +'-fps-'+str(fps)+ "." + extension
		set_fps(file_path, new_file_path, fps)

		#Calculate the vehicle count on the low encoding video
		vehicle_count_low_res = compute_vehicle_count(new_file_path, line_coordinates)

		os.remove(new_file_path)

		#If the error is within the threshold, then break
		detection_error = abs(vehicle_count_high_res-vehicle_count_low_res)/vehicle_count_high_res
		print(detection_error, THRESHOLD)
		if (detection_error <= THRESHOLD):
			return fps
		#If the count is outside the threshold, then increase the fps
		else:
			fps = fps+step

def calculate_encoding(file_path, original_file_name_for_coord):
	# file_name_with_ext = file_path.split("/")[-1] #With extension

	line_coordinates = getLineCoordinates(original_file_name_for_coord)
	
	#When coordinates are not found
	if not line_coordinates:
		print("Line coordinates not found")
		return

	#Calculate vehicle count in the original video
	vehicle_count_high_res = compute_vehicle_count(file_path, line_coordinates)

	br  = calculate_bitrate(file_path, line_coordinates, vehicle_count_high_res)
	fps = calculate_fps(file_path, line_coordinates, vehicle_count_high_res)
	res = calculate_resolution(file_path, line_coordinates, vehicle_count_high_res)
	
	return br, fps, res

# calculate_encoding("../streamed_files/nightSouthKorea.mov")