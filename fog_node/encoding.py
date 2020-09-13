import os

def get_param(message):
	'''
	Parse message of format: "<Parameter Name>-<numerical value>"
	:return: the numerical value as an integer
	'''
	return int(message.strip().split("-")[1])
def parse_response(server_response):
	'''
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
	'''
	# Parse the server message to extract the bitrate and fps
	bitrate, fps = parse_response(server_response)

	out_file_path = os.path.join("./encoded_videos","{}_{}.mp4".format(fog_name, camera_name))
	# Encoding the file
	os.system("ffmpeg -i {} -r {} -b:v {}k -an -y {} 2>/dev/null".format(file_path, fps, bitrate, out_file_path))

	##################################################HAS TO HAPPEN IN THE FINAL PRODUCT
	# Replace the original file with the encoded file
	# os.rename(out_file_path, file_path)
	return out_file_path ###########DONT DO THIS
