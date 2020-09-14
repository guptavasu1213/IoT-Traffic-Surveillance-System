import subprocess
import os
import argparse
from encoding import get_video_length

# Parsing the arguments to retrieve the camera and the fog name
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input_file_path", help="File path of the input video file", required=True)
ap.add_argument("-f", "--camera_folder_name", help="Camera folder name (Unique)", required=True)
ap.add_argument("-d", "--chunk_duration", help="Duration of each video segment", required=False, 
	default=1.0, type=float)
args = vars(ap.parse_args())


def main(input_file, camera_folder_name, seconds):
	"""
	Splits the input stream into multiple files with re-encoding
	:param input_file: input file path
	:param camera_folder_name: name of the folder which will contain the splitted camera videos
	:param seconds: the duration of each splitted video (in seconds)
	"""
	folder_path = "./surveillance-cam-videos/{}".format(camera_folder_name)
	extension = input_file[input_file.rfind(".")+1 : ]

	# Creating a folder for storing streamed videos	
	os.makedirs(folder_path, exist_ok=True)
		
	length_in_seconds = get_video_length(input_file)
	print(length_in_seconds)
	total_videos_to_create = int(int(length_in_seconds)//seconds)

	for i in range(total_videos_to_create):
		start_seconds = (i*seconds)

		# ffmpeg -ss <starting point> -i <input file> -t <duration of the clip> <output file>
		cmd = "ffmpeg -ss {} -i {} -t {} -y {}/{}.{} 2>/dev/null".format(str(start_seconds), input_file, 
			str(seconds), folder_path, str(i), extension)

		subprocess.run(cmd, shell=True)
		print(cmd)

	# For the last video:
	start_seconds = (total_videos_to_create) * seconds
	cmd = "ffmpeg -ss {} -i {} -t {} -y {}/{}.{} 2>/dev/null".format(str(start_seconds), input_file, 
		str(length_in_seconds-start_seconds), folder_path, str(total_videos_to_create), extension)

	subprocess.run(cmd, shell=True)
	print(cmd)

main(args["input_file_path"], args["camera_folder_name"], args["chunk_duration"])