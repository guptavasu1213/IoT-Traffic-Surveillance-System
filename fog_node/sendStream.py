from client import *
import os
import argparse

# Parsing the arguments to retrieve the camera and the fog name
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cameraName", help="Name of camera", required=True)
ap.add_argument("-f", "--fogName", help="Name of fog", required=True)
args = vars(ap.parse_args())

#Get the camera name from command line
cam_name = args["cameraName"]
fog_node_name = args["fogName"]

# cam_name = "cam2"
# fog_node_name = "fog1"

#Error check for the existence of camera folder
if cam_name not in os.listdir("./street-cam-videos"):
	print("Camera folder not found")
	exit(1)

#Error check for the existence of camera videos in its folder
if len(os.listdir("./street-cam-videos/"+cam_name)) == 0:
	print("No camera files in the folder")
	exit(1)

# Estabilish a connection with the server for the given fog and camera
client(fog_node_name, cam_name)