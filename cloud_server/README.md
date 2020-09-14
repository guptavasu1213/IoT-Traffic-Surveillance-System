# Cloud Server

## Overview

Cloud server receives the video streams and performs Traffic Density Measurement algorithm on them. If the encoding request is sent by the fog node, the cloud server computes the heuristic encoding parameters and sends them back to the fog node.

In the [detection_logs](https://github.com/guptavasu1213/IoT-Traffic-Surveillance-System/tree/master/cloud_server/detection_logs) folder, the results of the traffic density measurement algorithm can be found.

## Prerequisites
* OpenCV
* sklean
* pillow
* numpy 1.15.0
* torch 1.3.0
* tensorflow-gpu 1.13.1
* CUDA 10.0

```
pip3 install -r ./traffic_density_measurement_algorithm/requirements.txt
```

* Download YoloV4 model weights and move the in [this](https://github.com/guptavasu1213/IoT-Traffic-Surveillance-System/tree/master/cloud_server/traffic_density_measurement_algorithm/model_data) folder: [Click Here](https://drive.google.com/file/d/1RLSQB-SFWLsJlDKdoQe4zAOUe858ID2a/view?usp=sharing)

## Usage
In order to initialize the server, we run the following from the current folder:
* `--encoding_time` or `-et` is an optional argument used to pass the duration of video analysis to calculate the encoding parameters (in seconds) 
    ```
    python3 server.py [-et <encoding_time>]
    ```
* Example
    ```
    python3 server.py
    ```
    OR
    ```
    python3 server.py -et 20
    ```