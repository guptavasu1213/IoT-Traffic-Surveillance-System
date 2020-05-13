import subprocess
import ffmpeg
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_FPS

def remove_audio():
	pass

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
	Splits the input stream into multiple files
	:param input_stream: input file stream
	:param output_file: output file name
	:param seconds: the duration of each splitted video (in seconds)
	"""
	folder_name = input_file.split(".")[0]
	subprocess.run("mkdir " + folder_name, shell=True)

	output, extension = output_file.split(".")	
	
	start_seconds = 20
	
	length_in_seconds = get_video_length(input_file)
	total_videos_to_create = (int(length_in_seconds)//seconds) + 1
	i = 4
	# cmd = "ffmpeg -ss " + str(start_seconds) + " -i " + input_file + " -c copy"+ " -t " + str(length_in_seconds-start_seconds) + \
	# " " + folder_name + "/" +output+str(i+1)+"."+extension
	# subprocess.run(cmd, shell=True)
	# print(cmd)
	
	#############Works but inaccurate
	#ffmpeg -i bridge.mp4 -ss 20 -t 4.0300375469336664 -c copy bridge/output_file5.mp4
	cmd = "ffmpeg -i " + input_file + " -ss " + str(start_seconds) + " -t " + str(length_in_seconds-start_seconds) + \
	" -c:v copy -an " + folder_name + "/" +output+str(i+1)+"."+extension
	subprocess.run(cmd, shell=True)
	print(cmd)
	i=0
	# return
	for i in range(total_videos_to_create-1):
		start_seconds = (i*seconds)
		print(start_seconds)
		# i =0
		# (
		# 	input_stream
		# 		.filter("trim", start=start_seconds, duration=seconds)
		# 		.setpts ('PTS-STARTPTS') # resets the timestamp to 0 after a trim filter has been passed
		# 		.output(folder_name+str(i+1)+extension)
		# 		.run()
		# )
		# Example: ffmpeg -ss 0 -i bridge.mp4 -t 5 -vcodec copy bridge/output_file1.mp4

		##########Not working
		cmd = "ffmpeg -ss " + str(start_seconds) + " -i " + input_file + " -t " + str(seconds) + \
		" -vcodec copy " + folder_name + "/" +output+str(i+1)+"."+extension

		# cmd = "ffmpeg -i " + input_file + " -ss " + str(start_seconds) + " -to " + str(start_seconds+seconds) + \
		# " -vcodec copy -an " + folder_name + "/" +output+str(i+1)+"."+extension

		subprocess.run(cmd, shell=True)
		print(cmd)

input_file = "lowBridge.mp4"
input_stream = ffmpeg.input(input_file)
# print(length_in_seconds)
split_video_into_chunks(input_stream, input_file, "output_file.mp4", 5)
# inputStream.filter('fps', fps=1, round='up').output(outputFile).run()

# stream = ffmpeg.input('in.mp4')
# stream = ffmpeg.zoompan(stream, fps=10)
# stream = ffmpeg.output(stream, 'out.mp4')
# ffmpeg.run(stream)
#
# input_stream = ffmpeg.input('bridge.mp4')
# ffmpeg.input('bridge.mp4')

# .output('output.mp4').run()
