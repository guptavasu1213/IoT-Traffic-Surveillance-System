'''
This script is used to register new cameras on a fog node in the framework. The folders associated with the camera are
created and the line coordinates for traffic density measurement are set.
'''

import os
import argparse

# Parse the arguments to retrieve the camera and the fog name
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--camera_name", help="Name of camera", required=True)
ap.add_argument("-f", "--fog_name", help="Name of fog", required=True)
ap.add_argument("-lc", "--line_coordinates", help="Line Coordinates", required=True)
args = vars(ap.parse_args())

#Get the camera name from command line
camera_name = args["camera_name"]
fog_node_name = args["fog_name"]
coordinates = args["line_coordinates"]

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