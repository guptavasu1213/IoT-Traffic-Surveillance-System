import os
import subprocess
from timeit import time

import sys
import re

import tempfile

from video_encoding.encoding import *

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
			metadata['bitrate'] = re.search("bitrate: (\d+ kb/s)", l).group(0).split(':')[1].strip()
		if l.startswith('Stream #0:0'):
			metadata['video'] = {}
			metadata['video']['codec'], metadata['video']['profile'] = \
				[e.strip(' ,()') for e in re.search('Video: (.*? \(.*?\)),? ', l).group(0).split(':')[1].split('(')]
			metadata['video']['resolution'] = re.search('([1-9]\d+x\d+)', l).group(1)
			br = re.search('(\d+ kb/s)', l).group(1)
			metadata['video']['bitrate'] = br.split()[0]
			fps = re.search('(\d+ fps)', l).group(1)
			metadata['video']['fps'] = fps.split()[0]
	return metadata

def getLineCoordinates(coordinatesFile, fileNameIndex, newlineIndex):
	lineInFile = coordinatesFile[fileNameIndex:newlineIndex]
	lines = lineInFile[lineInFile.find(':')+1:]
	return lines    

def alterFPS(fileName, filePath):
	metadata = getVideoDetails(filePath)

	max_fps = 25
	min_fps = 7
	decreasingFactor = 3

	# Getting the video fps
	fps = int(metadata['video']['fps'])

	if (fps > max_fps):
		fps = max_fps
	elif (fps == max_fps):
		fps -= decreasingFactor

	#filename without extension
	extension = "." + fileName.split(".")[-1] 
	fileName = fileName.split(".")[0]

	#Make a directory for all different encodings for the same video
	os.makedirs(videoFolder+fileName+ "Videos", exist_ok=True)

	while fps >= min_fps:
		newFilePath = videoFolder +fileName+ "Videos/" + fileName + "-fps-" + str(fps) + extension
		print(newFilePath)

		start_conversion = time.time()
		# set_fps(filePath, newFilePath, fps)
		conversionTime = time.time() - start_conversion #Time for video re-encoding 

		fps = fps-decreasingFactor

		cmd = "python3 vehicle_counting_algorithm/main.py -i " + os.path.abspath(newFilePath) + " -t \"" + str(conversionTime) + \
				"\" -m \"" + video_metadata + "\" -l \"" + line_coordinates + "\""
		print("Running command:\n" + cmd)
		subprocess.run(cmd, shell=True)
		print("\n\n=========================================================\n\n")


#Open coordinates file
with open('streamed_files/coordinates.txt') as file:
	coordinatesFile = file.read()

videoFolder = "streamed_files/"
# Run detections on all files in the inputVideos directory
for fileName in os.listdir(videoFolder):
	filePath = videoFolder +fileName
	if (fileName == 'to-count' or fileName == 'done'):
		continue

	fileNameIndex = coordinatesFile.find(fileName)
	newlineIndex = coordinatesFile.find('\n', fileNameIndex)
	
	if fileNameIndex == -1:
		print("No line_coordinates found")
		continue

	line_coordinates = getLineCoordinates(coordinatesFile, fileNameIndex, newlineIndex)
	'''
	# Finding video resolution
	cmd = 'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 ' + filePath
	# out = subprocess.Popen(cmd.split(),
	#   stdout=subprocess.PIPE)
	# stdout, stderr = out.communicate()
	stdout = subprocess.check_output(cmd.split())
	resolution = stdout.decode('UTF-8').strip()
	print(resolution)

	
	# cmd = 'ffmpeg -i ../hq-videos/ChampsElysees_150610_03_Videvo.mov'
	cmd = 'ffmpeg -i ' + filePath
	print(cmd)
	# subprocess.run(cmd, shell=True)
	# stdout = subprocess.check_output(cmd.split())
	# print(stdout)
	out = subprocess.run(cmd,
		stdout = subprocess.PIPE,
		stderr=subprocess.STDOUT,
		shell=True)
	# stdout, stderr = out.communicate()
	output = out.stdout.decode('UTF-8').strip()
	brIndex = output.find('bitrate:')
	newlineIndex = output.find('\n', brIndex) 
	relevantPart = output[brIndex:newlineIndex]
	nums = [int(s) for s in relevantPart.split() if s.isdigit()]
	bitrate = nums[0]
	print(bitrate)
	'''
	#############################################################FPS

	alterFPS(fileName, filePath)

	
	#############################################################FPS   

	#===============================================================BITRATE
	'''
	metadata = getVideoDetails(filePath)

	# Getting the video bitrate
	bitrate = int(metadata['video']['bitrate'])
	if (bitrate > 1800):
		bitrate = 1800

	# 15% of the bitrate
	decreasingFactor = int(bitrate*0.15)
	#filename without extension

	extension = "." + fileName.split(".")[-1] 
	fileName = fileName.split(".")[0]

	#Make a directory for all different encodings for the same video
	os.makedirs(videoFolder+fileName+ "Videos", exist_ok=True)

	#Decrementing the bitrate for each 10%  
	while bitrate > 50:
		newFilePath = videoFolder +fileName+ "Videos/" + fileName + "-bitrate-" + str(bitrate) + extension
		print(newFilePath)

		start_conversion = time.time()
		set_bit_rate(filePath, newFilePath, bitrate)
		conversionTime = time.time() - start_conversion #Time for video re-encoding 

		if bitrate < 600:
			decreasingFactor = 100
		bitrate = bitrate-decreasingFactor
		print("---")

		video_metadata = str(getVideoDetails(newFilePath)['video'])
		# lastDotIndex = fileName.rfind(".")
		# print(fileName[:lastDotIndex])
		# print("python3 yolo_video.py --input inputVideos/" + fileName + " --output outputVideos/" + \
		#   fileName[:lastDotIndex] + ".avi --yolo yolo-coco --use-gpu 1")
		cmd = "python3 main.py -i " + newFilePath + " -t \"" + str(conversionTime) + \
				"\" -m \"" + video_metadata + "\" -l \"" + line_coordinates + "\""
		print("Running command:\n" + cmd)
		subprocess.run(cmd, shell=True)
		print("\n\n=========================================================\n\n")
	'''    
	#===============================================================BITRATE

	'''
	###############################################################RESOLUTION
	metadata = getVideoDetails(filePath)

	# Getting the video resolution
	resolution = [int(val) for val in metadata['video']['resolution'].strip().split('x')]
	print(resolution)
	resolutionWidth = resolution[0]

	#Capping the width
	if (resolutionWidth > 1920):
		resolutionWidth = 1920

	# 20% of the resolution
	decreasingFactor = int(resolutionWidth*0.2)

	if resolutionWidth == resolution[0]:
		resolutionWidth = resolutionWidth-decreasingFactor

	#filename without extension
	extension = "." + fileName.split(".")[-1] 
	fileName = fileName.split(".")[0]

	#Make a directory for all different encodings for the same video
	os.makedirs(videoFolder+fileName+ "Videos", exist_ok=True)

	#Decrementing the resolution for each 20%  
	while resolutionWidth > 200:
		newFilePath = videoFolder +fileName+ "Videos/" + fileName + "-resolutionWidth-" + str(resolutionWidth) + extension
		print(newFilePath)

		start_conversion = time.time()

		#When conversion is unsuccessful        
		if not set_resolution(filePath, newFilePath, resolutionWidth):
			# When an issue occurs while retrieving the video codec information, 
			# it means that the video conversion as not successful with the given resolution
			resolutionWidth -= 1
			continue

		conversionTime = time.time() - start_conversion #Time for video re-encoding 

		video_metadata = getVideoDetails(newFilePath)['video']
			
		if resolutionWidth < 700:
			decreasingFactor = 100
		resolutionWidth = resolutionWidth-decreasingFactor

		print("---")

		# Getting the video resolution
		currentResolution = [int(val) for val in video_metadata['resolution'].strip().split('x')]

		# lc = str(format_coordinates(line_coordinates, resolution, currentResolution))
		
		# lastDotIndex = fileName.rfind(".")
		# print(fileName[:lastDotIndex])
		# print("python3 yolo_video.py --input inputVideos/" + fileName + " --output outputVideos/" + \
		#   fileName[:lastDotIndex] + ".avi --yolo yolo-coco --use-gpu 1")
		cmd = "python3 main.py -i " + newFilePath + " -t \"" + str(conversionTime) + \
				"\" -m \"" + str(video_metadata) + "\" -l \"" + str(line_coordinates) + "\"" + \
				" -r \"" + metadata['video']['resolution'] + "\" -c \"" + video_metadata['resolution'] + "\""
		print("Running command:\n" + cmd)
		subprocess.run(cmd, shell=True)
		print("\n\n=========================================================\n\n")
		###############################################################RESOLUTION

	'''