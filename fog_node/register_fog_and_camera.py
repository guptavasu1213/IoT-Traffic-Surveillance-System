import socket
import sys

import argparse

# Parsing the arguments to retrieve the camera and the fog name
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--camera_name", help="Name of camera", required=True)
ap.add_argument("-f", "--fog_name", help="Name of fog", required=True)
ap.add_argument("-lc", "--line_coordinates", help="Line Coordinates for Counting", required=True)
ap.add_argument("-ip", "--ip_address", help="IP Address of the server", required=True)
ap.add_argument("-pn", "--port_number", help="Port Number of the server", required=True, type=int)
args = vars(ap.parse_args())

registration_message = "REGISTER CAM~{}~{}~{}".format(args["fog_name"].strip(),
	args["camera_name"].strip(), args["line_coordinates"].strip())

#Create client socket that using IPv4 and TCP protocols
try:
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
	print('Error in client socket creation:',e)
	sys.exit(1)

try:
	#Client connect with the server
	clientSocket.connect((args["ip_address"], args["port_number"]))

	#Send Registation Message
	clientSocket.send(registration_message.encode('ascii'))

	clientSocket.close()

except socket.error as e:
	print('An error occurred:',e)
	clientSocket.close()
	sys.exit(1)

print("Registation Message Sent!")
