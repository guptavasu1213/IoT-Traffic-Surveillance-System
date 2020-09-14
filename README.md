# IoT Traffic Surveillance System using Adaptive Video Encoding

## Overview

This repository contains the code for an IoT Traffic Surveillance System using a fog-computing architecture as shown by the image below. The system uses an adaptive video encoding algorithm that switches the video encoding at specific intervals to reduce the required network bandwidth. The repository also contains a Traffic Density Measument algorithm to analyze the surveillance videos.

<p align="center">
  <img src="https://github.com/guptavasu1213/IoT-Traffic-Surveillance-System/blob/master/system_overview_diagram.jpg">
</p>

## Prerequisites

* Linux distro or MacOS (Tested on Ubuntu 18.04 and Ubuntu 20.04.1 LTS)

The following dependencies are common between the Fog Nodes and the Cloud Server:

* FFmpeg (Tested on 4.1.4)
```
sudo snap install ffmpeg
```
* Python3 (Tested on Python 3.6.9)

```
sudo apt-get upgrade python3
```
* Clone this repository and put the `cloud_server` folder on the server machine, and the `fog_node` folder on the fog node machine.

## Usage
* For running the Cloud Server scripts, refer to the [README.md](https://github.com/guptavasu1213/IoT-Traffic-Surveillance-System/blob/master/cloud_server/README.md)
* For running the Fog Node scripts, refer to the [README.md](https://github.com/guptavasu1213/IoT-Traffic-Surveillance-System/blob/master/fog_node/README.md) 

## Project Status 

Complete