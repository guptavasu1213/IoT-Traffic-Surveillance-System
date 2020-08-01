import subprocess
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_FPS

def remove_audio(input_file, output_file):
	"""
	Removing the audio from the input file and saves it as the output file.
	The file is not re-encoded as the video encoding scheme is copied.
	:param input_file: input file name
	:param output_file: output file name
	"""
	cmd = "ffmpeg -i " + input_file + " -c:v copy -an " + output_file	
	subprocess.run(cmd, shell=True)
	print(cmd)

def set_fps(input_file, output_file, new_fps):
	"""
	:param input_file: input file name
	:param output_file: output file name
	"""
	video = VideoCapture(input_file)
	input_fps = video.get(CAP_PROP_FPS)
	if (new_fps >= input_fps):
		print("The fps is greater than or equal to the original video, so no change is made")
		return

	cmd = "ffmpeg -i " + input_file + " -r " + str(new_fps) + " -an -y " + output_file	
	subprocess.run(cmd, shell=True)
	print(cmd)

def set_resolution(input, output, resolution):
	'''
	Returns false when unsuccessful
	Returns true when successful
	'''
	cmd = "ffmpeg -i " + input + " -vf scale=" + str(resolution) + ":-1 -an -y " + output 
	print(cmd)
	try:
		subprocess.check_output(cmd, shell=True)
		return True
	except:
		return False
def set_bitrate(input, output, bitrate):
	cmd = "ffmpeg -i " + input + " -b:v " + str(bitrate) + "k -an -y " + output 
	subprocess.run(cmd, shell=True)
	print(cmd)

# Learn more about different ways of compressing ###
# Using H.265 by default
def compress(input_file, output_file, encoding="libx265"):
	"""
	:param input_file: input file name
	:param output_file: output file name
	"""	
	#################################################Quantization factor can also be added
	# Example: ffmpeg -i bridge.mp4 -vcodec libx265 [-crf 28] lowBridge.mp4
	cmd = "ffmpeg -i " + input_file + " -vcodec " + encoding + " " + output_file	
	subprocess.run(cmd, shell=True)
	print(cmd)

def get_video_length(input_file):
	"""
	:param input_file:
	:return: Total video length in seconds
	"""
	video = VideoCapture(input_file)
	fps = video.get(CAP_PROP_FPS)
	total_frames = video.get(CAP_PROP_FRAME_COUNT)
	return float(total_frames) / float(fps)

def trim_video(input_file, output_file, start_time, length_in_seconds):
	'''
	Trims a video (without re-encoding) with the given start and the length of clip
	'''
	cmd = "ffmpeg -ss " + str(start_time) + " -i " + input_file + " -c copy -t " + str(length_in_seconds) + \
			" -y " + output_file	
	subprocess.run(cmd, shell=True)

	print(cmd)

def split_video_into_chunks(input_file, output_file, seconds):
	"""
	Splits the input stream into multiple files with re-encoding
	:param input_file: input file name
	:param output_file: output file name
	:param seconds: the duration of each splitted video (in seconds)
	"""
	folder_name = input_file.split(".")[0]
	subprocess.run("mkdir " + folder_name, shell=True) # Creating a folder with the same name as the input video

	output, extension = output_file.split(".")	
		
	length_in_seconds = get_video_length(input_file)
	total_videos_to_create = (int(length_in_seconds)//seconds) + 1

	for i in range(total_videos_to_create-1):
		start_seconds = (i*seconds)

		# ffmpeg -ss <starting point> -i <input file> -t <duration of the clip> <output file>
		cmd = "ffmpeg -ss " + str(start_seconds) + " -i " + input_file + " -t " + str(seconds) + \
			" -y " + folder_name + "/" + output + str(i+1) + "." +extension
		subprocess.run(cmd, shell=True)
		print(cmd)

	# For the last video:
	start_seconds = (total_videos_to_create-1) * seconds
	cmd = "ffmpeg -ss " + str(start_seconds) + " -i " + input_file + " -t " + str(length_in_seconds-start_seconds) + \
	" -y " + folder_name + "/" +output+str(total_videos_to_create)+"."+extension
	subprocess.run(cmd, shell=True)
	print(cmd)


# input_file = "lowBridge.mp4"

# split_video_into_chunks(input_file, "output_file.mp4", 5)
# remove_audio(input_file, "silentFile.mp4")
# reduceFPS("sd",'sddsds',12)
