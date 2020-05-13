import subprocess
import ffmpeg
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

def reduceFPS():
	pass

def decreaseBitRate():
	pass

def changeFormat():
	pass

#Learn more about different ways of compressing 
def compress():
	pass

def get_video_length(input_file):
	"""
	:param input_file:
	:return: Total video length in seconds
	"""
	video = VideoCapture(input_file)
	fps = video.get(CAP_PROP_FPS)
	total_frames = video.get(CAP_PROP_FRAME_COUNT)
	return float(total_frames) / float(fps)


def split_video_into_chunks(input_stream, input_file, output_file, seconds):
	"""
	Splits the input stream into multiple files with re-encoding
	:param input_stream: input file stream
	:param input_file: input file name
	:param output_file: output file name
	:param seconds: the duration of each splitted video (in seconds)
	"""
	folder_name = input_file.split(".")[0]
	subprocess.run("mkdir " + folder_name, shell=True) # Creating a folder with the same name as the input video

	output, extension = output_file.split(".")	
		
	length_in_seconds = get_video_length(input_file)
	total_videos_to_create = (int(length_in_seconds)//seconds) + 1

	# cmd = "ffmpeg -ss " + str(start_seconds) + " -i " + input_file + " -c copy"+ " -t " + str(length_in_seconds-start_seconds) + \
	# " " + folder_name + "/" +output+str(i+1)+"."+extension
	# subprocess.run(cmd, shell=True)
	# print(cmd)
	
	#############Works but inaccurate
	#ffmpeg -i bridge.mp4 -ss 20 -t 4.0300375469336664 -c copy bridge/output_file5.mp4
	# # cmd = "ffmpeg -i " + input_file + " -ss " + str(start_seconds) + " -t " + str(length_in_seconds-start_seconds) + \
	# # " -c:v copy -an " + folder_name + "/" +output+str(i+1)+"."+extension
	# subprocess.run(cmd, shell=True)
	# print(cmd)
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

		# OTHER WAY
		# (
		# 	input_stream
		# 		.filter("trim", start=start_seconds, duration=seconds)
		# 		.setpts ('PTS-STARTPTS') # resets the timestamp to 0 after a trim filter has been passed
		# 		.output(folder_name+str(i+1)+extension)
		# 		.run()
		# )
		# Example: ffmpeg -ss 0 -i bridge.mp4 -t 5 -vcodec copy bridge/output_file1.mp4

		##########Not working
		# cmd = "ffmpeg -ss " + str(start_seconds) + " -i " + input_file + " -t " + str(seconds) + \
		# " -vcodec copy " + folder_name + "/" +output+str(i+1)+"."+extension

		# NOt working with the same encoding
		# cmd = "ffmpeg -i " + input_file + " -ss " + str(start_seconds) + " -to " + str(start_seconds+seconds) + \
		# " -vcodec copy -an " + folder_name + "/" +output+str(i+1)+"."+extension


input_file = "lowBridge.mp4"
input_stream = ffmpeg.input(input_file)
# print(length_in_seconds)
split_video_into_chunks(input_stream, input_file, "output_file.mp4", 5)
# inputStream.filter('fps', fps=1, round='up').output(outputFile).run()
remove_audio(input_file, "silentFile.mp4")
# stream = ffmpeg.input('in.mp4')
# stream = ffmpeg.zoompan(stream, fps=10)
# stream = ffmpeg.output(stream, 'out.mp4')
# ffmpeg.run(stream)
#
# input_stream = ffmpeg.input('bridge.mp4')
# ffmpeg.input('bridge.mp4')

# .output('output.mp4').run()
