# Fog Node


## Overview

The fog nodes streams the surveillance videos to the cloud server in low or high resolution depending on the situation. Initially, the videos get streamed at high resolution as the heuristic encoding parameters are calculated by the cloud server. After these parameters are calculated by the cloud server and are recieved by the fog node, the following videos are streamed at a lower encoding quality for a specific time.


## Prerequisites
If you choose to try your own Traffic Surveillance Video follow these steps:
* The cloud server needs to register the fog node and camera and add them to its known clients. 
```
python3 register_fog_and_camera.py -f <fog_name> -c <camera_name> -l <line_coordinates>
```
* Example
```
python3 register_fog_and_camera.py -c cam9 -f fog7 -ip "199.116.235.176" -pn 12000 -lc "0,0,50,50; 25,67,75,97"
```
* Install Pip3
```
sudo apt-get install python3-pip
```
* Install OpenCV (Tested on OpenCV 3.4.2.17)
```
pip3 install opencv-python==3.4.2.17
```
* You need to split your video in one-second chunks to provide a live-stream experience on the cloud server. This can be done using the code below:
	* `--input_file_path` or `-i` argument is required to pass the input file path
	* `camera_folder_name` or `-f` argument is required to pass the camera folder name where the videos are going to be stored.
	* `chunk_duration` or `-d` argument is optional to pass the duration each video segment. By default is 1 second.
	
	```
	python3 split_video_into_chunks.py -i <input_video_path> -c <camera_folder_name> [-d <duration_in_seconds>]
	```

	Example:
	```
	python3 split_video_into_chunks.py -i video.mp4 -c cam1
	```

## Usage
To stream the videos to the cloud server using our framework, follow these instructions:
* `--camera_name` or `-c` argument requires the name of the camera whose streams have to be sent to the cloud server
* `--fog_name` or `-f` argument requires the name of the current fog node 
* `--ip_address` or `-ip` argument requires the IP address of the server to connect with
* `--port_number` or `-pn` argument requires the Port Number of the server to connect with
* `--encoding_interval` or `-ei` argument is optional to pass where it specifies the time interval (in minutes) after which the encoding calculation request is sent to the server. The default time is 60 minutes.

```
python3 send_stream.py -c <camera_name> -f <fog_name> -ip <ip_address> -pn <port_number>
```

## Example
```
python3 send_stream.py -c cam2 -f fog1 -ip "199.116.235.176" -pn 12000
```