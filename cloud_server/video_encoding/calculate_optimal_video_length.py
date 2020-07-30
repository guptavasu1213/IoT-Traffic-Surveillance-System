'''
This file is not used in the deployment. The sole purpose of this file is to calculate the optimal time for the videos to calculate the encoding parameters.
'''

# Segment file in two pieces of different lengths: 1 min and 4 mins
from calculate_encoding_setting import *
from encoding import *
import csv

#Open coordinates file
with open('../streamed_files/coordinates.txt') as file:
	coordinatesFile = file.read()

videoFolder = "../streamed_files/"
# Run detections on all files in the inputVideos directory
for fileName in os.listdir(videoFolder):
	input_filepath = videoFolder + fileName
	if (fileName == 'to-count' or fileName == 'done' or fileName == "kukuNew.mp4"):
		continue

	fileNameIndex = coordinatesFile.find(fileName)
	newlineIndex = coordinatesFile.find('\n', fileNameIndex)
	
	if fileNameIndex == -1:
		print("No line_coordinates found")
		continue

	small_filepath = "./trimmed_videos/smallTrimmedClip.mp4"
	big_filepath = "./trimmed_videos/largeTrimmedClip.mp4"

	num_mins = 4
	start_clip_length = 60

	trim_video(input_filepath, small_filepath, "00:00", start_clip_length)
	trim_video(input_filepath, big_filepath, "01:00", (60*num_mins))

	# Calculating the best encoding params for the original small video segment 
	fps, bitrate, resolution_width = calculate_encoding(small_filepath, fileName)
	#========== Testing the encoding parameters
	line_coordinates = getLineCoordinates(fileName)

	#When coordinates are not found
	if not line_coordinates:
		print("Coordinates not found")
		continue

	#Test the encoding parameters on the original video
	original_count = compute_vehicle_count(big_filepath, line_coordinates)

	#Test the results on fps
	fps_path = "./trimmed_videos/largeTrimmedClip-fps.mp4"
	set_fps(big_filepath, fps_path, fps)
	fps_count = compute_vehicle_count(fps_path, line_coordinates)

	#Test the results on bitrate
	br_path = "./trimmed_videos/largeTrimmedClip-bitrate.mp4"
	set_bitrate(big_filepath, br_path, bitrate)
	br_count = compute_vehicle_count(br_path, line_coordinates)

	#Test the results on res
	res_path = "./trimmed_videos/largeTrimmedClip-resolution.mp4"
	set_resolution(big_filepath, res_path, resolution_width)

	originalResolution = getFileResolution(big_filepath)
	decreasedResolution = getFileResolution(res_path)

	resolutionRatio = str(decreasedResolution[0]/originalResolution[0])+'x'+str(decreasedResolution[1]/originalResolution[1])

	res_count = compute_vehicle_count(res_path, line_coordinates, resolutionRatio)

	#Log the counts in a file
	with open("./count_logs/optimal_param_count.csv", 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow([fileName, str(start_clip_length), str(original_count), str(fps_count), str(br_count), str(res_count)])
