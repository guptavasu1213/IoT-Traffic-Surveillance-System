from client import *
import os
import argparse

# Parsing the arguments to retrieve the camera and the fog name
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--camera_name", help="Name of camera", required=True)
ap.add_argument("-f", "--fog_name", help="Name of fog", required=True)
ap.add_argument("-ip", "--ip_address", help="IP Address of the server", required=True)
ap.add_argument("-pn", "--port_number", help="Port Number of the server", required=True, type=int)
ap.add_argument("-ei", "--encoding_interval", help="Time interval for encoding calculation (in minutes)", required=False, default=60, type=int)
args = vars(ap.parse_args())

#Get the camera name from command line
cam_name = args["camera_name"]
fog_node_name = args["fog_name"]

#Error check for the existence of camera folder
if cam_name not in os.listdir("./surveillance-cam-videos"):
	print("Camera folder not found")
	exit(1)

#Error check for the existence of camera videos in its folder
if len(os.listdir("./surveillance-cam-videos/"+cam_name)) == 0:
	print("No camera files in the folder")
	exit(1)

# Establish a connection with the server for the given fog and camera
client(fog_node_name, cam_name, args["ip_address"], args["port_number"], args["encoding_interval"]*60)