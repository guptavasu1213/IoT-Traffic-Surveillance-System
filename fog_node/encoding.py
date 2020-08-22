import os
# import time
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
	# print("{} {}".format(bitrate, fps))
	return bitrate, fps

def encode_video(file_path, server_response, fog_name, camera_name):
	# get file name
	# Parse the response message
	# Encode according to the response in a temp file
	# Replace the temp file with the actual file
	bitrate, fps = parse_response(server_response)

	out_file_path = os.path.join("./encoded_videos","{}_{}.mp4".format(fog_name, camera_name))
	# start = time.time()
	os.system("ffmpeg -i {} -r {} -b:v {}k -an -y {} 2>/dev/null".format(file_path, fps, bitrate, out_file_path))
	# print("===> TOOK:", time.time()-start)

	##################################################HAS TO HAPPEN IN THE FINAL PRODUCT
	# Replace the original file with the encoded file
	# os.rename(out_file_path, file_path)
	return out_file_path ###########DONT DO THIS

# encode_video("1.mp4", "Parameters: Bitrate-100; FPS-10")
