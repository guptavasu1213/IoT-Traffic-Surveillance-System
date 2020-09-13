# Cloud Server

## Overview

Cloud server receives the video streams and performs Traffic Density Measurement algorithm on them. If the encoding request is sent by the fog node, the cloud server computes the heuristic encoding parameters and sends them back to the fog node.

In the [detection_logs](https://github.com/guptavasu1213/IoT-Traffic-Surveillance-System/tree/master/cloud_server/detection_logs) folder, the results of the traffic density measurement algorithm can be found.

## Prerequisites
* OpenCV
* Tracking algo already has everything listed#############

## Usage
In order to initialize the server, we run the following from the current folder:
```
python3 server.py
```
