'''
This file is not used in the deployment. The sole purpose of this file is to calculate the optimal time for the videos to calculate the encoding parameters.
'''

# Segment file in two pieces of different lengths: 1 min and 4 mins
from calculate_encoding_setting import *
from encoding import *
import csv
import time

#Open coordinates file
with open('../streamed_files/coordinates.txt') as file:
	coordinatesFile = file.read()

timings = [[15, "00:15", 300-15], [30, "00:30", 300-30], [45, "00:45", 300-45], [60, "01:00", 300-60], [75, "01:15", 300-75], [90, "01:30", 300-90]]

videoFolder = "../streamed_files/"
# Run detections on all files in the inputVideos directory
for fileName in os.listdir(videoFolder):
	for timing in timings:
		start_time = time.time()

		input_filepath = videoFolder + fileName
		if (fileName == 'to-count' or fileName == 'done'):
			continue

		fileNameIndex = coordinatesFile.find(fileName)
		newlineIndex = coordinatesFile.find('\n', fileNameIndex)
		
		if fileNameIndex == -1:
			print("No line_coordinates found")
			continue

		small_filepath = "./trimmed_videos/smallTrimmedClip.mp4"
		big_filepath = "./trimmed_videos/largeTrimmedClip.mp4"
		
		start_clip_length, line_2_start, line_2_end = timing

		trim_video(input_filepath, small_filepath, "00:00", start_clip_length)
		trim_video(input_filepath, big_filepath, line_2_start, line_2_end)

		time_encoding_calculate = time.time()
		# Calculating the best encoding params for the original small video segment 
		bitrate, fps, resolution_width = calculate_encoding(small_filepath, fileName)
		time_encoding_calculate = time_encoding_calculate - time.time()
		#========== Testing the encoding parameters
		line_coordinates = getLineCoordinates(fileName)

		#When coordinates are not found
		if not line_coordinates:
			print("Coordinates not found")
			continue

		#Test the encoding parameters on the original video
		time_vehicle_count = time.time()
		original_count = compute_vehicle_count(big_filepath, line_coordinates)
		time_vehicle_count = time_vehicle_count - time.time()

		#Test the results on fps
		time_fps_calculate = time.time()
		fps_path = "./trimmed_videos/largeTrimmedClip-fps.mp4"
		set_fps(big_filepath, fps_path, fps)
		fps_count = compute_vehicle_count(fps_path, line_coordinates)
		time_fps_calculate = time_fps_calculate - time.time()

		#Test the results on bitrate
		time_br_calculate = time.time()
		br_path = "./trimmed_videos/largeTrimmedClip-bitrate.mp4"
		set_bitrate(big_filepath, br_path, bitrate)
		br_count = compute_vehicle_count(br_path, line_coordinates)
		time_br_calculate = time_br_calculate - time.time()

		#Test the results on res
		time_resol_calculate = time.time()
		res_path = "./trimmed_videos/largeTrimmedClip-resolution.mp4"
		set_resolution(big_filepath, res_path, resolution_width)

		originalResolution = getFileResolution(big_filepath)
		decreasedResolution = getFileResolution(res_path)

		resolutionRatio = str(decreasedResolution[0]/originalResolution[0])+'x'+str(decreasedResolution[1]/originalResolution[1])

		res_count = compute_vehicle_count(res_path, line_coordinates, resolutionRatio)
		time_resol_calculate = time_resol_calculate - time.time()

		computation_time = time.time() - start_time
		#Log the counts in a file
		with open("./count_logs/optimal_param_count-new.csv", 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow([fileName, str(start_clip_length), str(original_count), str(fps_count), \
			str(br_count), str(res_count), str(bitrate), str(fps), str(resolution_width), str(computation_time),\
				str(time_encoding_calculate), str(time_vehicle_count), str(time_fps_calculate), str(time_br_calculate),\
					str(time_resol_calculate)])
