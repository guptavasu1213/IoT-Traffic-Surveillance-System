import os
from cv2 import VideoCapture, CAP_PROP_FRAME_COUNT, CAP_PROP_FPS

def get_video_length(input_file):
	'''
	:param input_file: Path of the input file whose length needs to be found
	:return: Total video length in seconds
	'''
	video = VideoCapture(input_file)
	fps = video.get(CAP_PROP_FPS)
	total_frames = video.get(CAP_PROP_FRAME_COUNT)
	return float(total_frames) / float(fps)

def get_param(message):
	'''
	Parse message of format: "<Parameter Name>-<numerical value>"
	:return: the numerical value as an integer
	'''
	return int(message.strip().split("-")[1])
def parse_response(server_response):
	'''
	:param server_response: Message sent by the server.
	The message is of the format: "Parameters: <Parameter Name>-<numerical value>;
	<Parameter Name>-<numerical value>"
	'''
	params = server_response.split(":")[1].strip()
	params = params.split(';')
	bitrate = get_param(params[0])
	fps = get_param(params[1])
	return bitrate, fps

def encode_video(file_path, server_response, fog_name, camera_name):
	'''
	Encoding the file based on the parameters in the server response message.
	:param file_path: Path of the file to be encoded
	:param server_response: The response message from the cloud server containing
	information about the encoding parameters
	:param fog_name: The name of the fog node
	:param camera_name: The name of the camera
	:return: path of the output encoded file
	'''
	# Parse the server message to extract the bitrate and fps
	bitrate, fps = parse_response(server_response)

	out_file_path = os.path.join("./encoded_videos","{}_{}.mp4".format(fog_name, camera_name))
	# Encoding the file
	os.system("ffmpeg -i {} -r {} -b:v {}k -an -y {} 2>/dev/null".format(file_path, fps, bitrate, out_file_path))

	return out_file_path
