from client import *
import os
import argparse
#Get the camera name from command line

cam_name = "cam3"
fog_node_name = "fog1"

#Error check for the existence of camera folder
if cam_name not in os.listdir("./street-cam-videos"):
	print("Camera folder not found")
	exit(1)

#Error check for the existence of camera videos in its folder
if len(os.listdir("./street-cam-videos/"+cam_name)) == 0:
	print("No camera files in the folder")
	exit(1)

client(fog_node_name, cam_name)