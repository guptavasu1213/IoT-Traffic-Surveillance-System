'''
This script is used to register new cameras on a fog node in the framework. The folders associated with the camera are
created and the line coordinates for traffic density measurement are set.
'''

import os

def register(fog_node_name, camera_name, coordinates):
	'''
	Register the camera with the given coordinates
	'''
	#Create folders for fog node and camera in the framework
	path = os.path.join("encoding_videos", fog_node_name, camera_name, "videos")
	os.makedirs(path, exist_ok=True)

	path = os.path.join("detection_logs", fog_node_name, camera_name)
	os.makedirs(path, exist_ok=True)

	path = os.path.join("streamed_files", fog_node_name, camera_name)
	os.makedirs(path, exist_ok=True)

	#Write coordinates for the camera in a text file
	with open(os.path.join("streamed_files", fog_node_name, "line_coordinates.txt"), "a") as file:
		file.write("{}:{}".format(camera_name, coordinates.strip()))

	print("All files and directories have been successfully created!")