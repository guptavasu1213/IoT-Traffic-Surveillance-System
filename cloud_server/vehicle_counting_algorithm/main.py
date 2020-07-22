#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import sys
#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import os
import datetime
from timeit import time
import warnings
import cv2
import numpy as np
import argparse
from PIL import Image
from yolo import YOLO

from deep_sort import preprocessing
from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from tools import generate_detections as gdet
from deep_sort.detection import Detection as ddet
from collections import deque
from keras import backend
import tensorflow as tf
from tensorflow.compat.v1 import InteractiveSession
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
from counter import *
from introffmpeg import get_video_length

def format_coordinates(lines, originalResolution, currentResolution):
    originalResolution = [int(val) for val in originalResolution.strip().split('x')]
    currentResolution = [int(val) for val in currentResolution.strip().split('x')]

    line_coord = []
    for val in lines.split(";"):
        line_coord.append([])
        points = val.strip().split(',')
        for i in range(2):
            # line_coord[-1].append((int(points[i*2].strip()), int(points[(i*2)+1].strip())))            
            p = (int(points[i*2].strip()), int(points[(i*2)+1].strip()))
            # print(p)
            p = (int((p[0]/originalResolution[0])*currentResolution[0]), int((p[1]/originalResolution[1])*currentResolution[1]))
            line_coord[-1].append(p)
    print(line_coord, '=======', currentResolution, originalResolution)
    return line_coord

# PURPOSE: Displaying the FPS of the detected video
# PARAMETERS: Start time of the frame, number of frames within the same second
# RETURN: New start time, new number of frames 
def displayFPS(start_time, num_frames):
    current_time = int(time.time())
    time_elapsed = current_time - start_time
    if(current_time > start_time):
        fps  = num_frames/time_elapsed
        print("FPS:", fps)


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input",help="path to input video", required=True)
ap.add_argument("-m", "--metadata",help="encoding params")
ap.add_argument("-l", "--coordinates",help="coordinates")
ap.add_argument("-s", "--size",help="input file size")
ap.add_argument("-t", "--time",help="conversion time for video")
ap.add_argument("-r", "--OriginalResolution",help="Original video resolution")
ap.add_argument("-c", "--CurrentResolution",help="current video resolution")

args = vars(ap.parse_args())

pts = [deque(maxlen=30) for _ in range(9999)]
warnings.filterwarnings('ignore')

# initialize a list of colors to represent each possible class label
np.random.seed(100)
COLORS = np.random.randint(0, 255, size=(200, 3),
	dtype="uint8")

line_coordinates = format_coordinates(args['coordinates'], args['OriginalResolution'], args['CurrentResolution'])

def main(yolo):

    start = time.time()
    max_cosine_distance = 0.3
    nn_budget = None
    nms_max_overlap = 1.0

    counter = []
    #deep_sort
    model_filename = 'model_data/market1501.pb'
    encoder = gdet.create_box_encoder(model_filename,batch_size=1)

    metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
    tracker = Tracker(metric)

    writeVideo_flag = True
    video_capture = cv2.VideoCapture(args["input"])
    fps = video_capture.get(cv2.CAP_PROP_FPS)


    if writeVideo_flag:
    # Define the codec and create VideoWriter object
        w = int(video_capture.get(3))
        h = int(video_capture.get(4))
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter('./output/output.avi', fourcc, fps, (w, h))
        list_file = open('detection_rslt.txt', 'w')
        frame_index = -1

    fps = 0.0
    start_time = int(time.time())
    num_frames = 0
    vehicle_count = 0

    # Line intersection counter
    line_counter = Counter(line_coordinates)

    # main loop
    while True:
        os.system('clear')
        num_frames+= 1
        print("Current Frame:\t", str(num_frames) + '/' + str(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)))
        #Calculating fps each second
        displayFPS(start_time, num_frames)

        ret, frame = video_capture.read()  # frame shape 640*480*3
        if ret != True:
            break
        t1 = time.time()

        #image = Image.fromarray(frame)
        image = Image.fromarray(frame[...,::-1]) #bgr to rgb
        boxs, confidence, class_names = yolo.detect_image(image)
        features = encoder(frame,boxs)
        # score to 1.0 here).
        detections = [Detection(bbox, 1.0, feature) for bbox, feature in zip(boxs, features)]
        # Run non-maxima suppression.
        boxes = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        indices = preprocessing.non_max_suppression(boxes, nms_max_overlap, scores)
        detections = [detections[i] for i in indices]

        # Call the tracker
        tracker.predict()
        tracker.update(detections)

        i = int(0)
        indexIDs = []
        c = []
        boxes = []

        for det in detections:
            bbox = det.to_tlbr()
            cv2.rectangle(frame,(int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])),(255,255,255), 2)
            #print(class_names)
            #print(class_names[p])

        for track in tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue
            #boxes.append([track[0], track[1], track[2], track[3]])
            indexIDs.append(int(track.track_id))
            counter.append(int(track.track_id))
            bbox = track.to_tlbr()
            color = [int(c) for c in COLORS[indexIDs[i] % len(COLORS)]]
            #print(frame_index)
            list_file.write(str(frame_index)+',')
            list_file.write(str(track.track_id)+',')
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])),(color), 3)
            b0 = str(bbox[0])#.split('.')[0] + '.' + str(bbox[0]).split('.')[0][:1]
            b1 = str(bbox[1])#.split('.')[0] + '.' + str(bbox[1]).split('.')[0][:1]
            b2 = str(bbox[2]-bbox[0])#.split('.')[0] + '.' + str(bbox[3]).split('.')[0][:1]
            b3 = str(bbox[3]-bbox[1])

            list_file.write(str(b0) + ','+str(b1) + ','+str(b2) + ','+str(b3))
            #print(str(track.track_id))
            list_file.write('\n')
            #list_file.write(str(track.track_id)+',')
            cv2.putText(frame,str(track.track_id),(int(bbox[0]), int(bbox[1] -50)),0, 5e-3 * 150, (color),2)
            if len(class_names) > 0:
               class_name = class_names[0]
               cv2.putText(frame, str(class_names[0]),(int(bbox[0]), int(bbox[1] -20)),0, 5e-3 * 150, (color),2)

            i += 1
            #bbox_center_point(x,y)
            center = (int(((bbox[0])+(bbox[2]))/2),int(((bbox[1])+(bbox[3]))/2))
            #track_id[center]

            pts[track.track_id].append(center)

            thickness = 5
            #center point
            cv2.circle(frame, (center), 1, color, thickness)

            # print("=================?????", track.track_id, line_counter.trackedID)

            # If the box intersects with the line
            if line_counter.intersects_with_bbox(bbox) and track.track_id not in line_counter.trackedID:
                line_counter.addToTrackedList(track.track_id)
                vehicle_count+=1

			# draw motion path
            for j in range(1, len(pts[track.track_id])):
                if pts[track.track_id][j - 1] is None or pts[track.track_id][j] is None:
                   continue
                thickness = int(np.sqrt(64 / float(j + 1)) * 2)
                cv2.line(frame,(pts[track.track_id][j-1]), (pts[track.track_id][j]),(color),thickness)
                #cv2.putText(frame, str(class_names[j]),(int(bbox[0]), int(bbox[1] -20)),0, 5e-3 * 150, (255,255,255),2)

        count = len(set(counter))
        cv2.putText(frame, "Total Line Counter: "+str(vehicle_count),(int(20), int(120)),0, 5e-3 * 200, (0,255,0),2)
        # cv2.putText(frame, "Total Counter: "+str(count),(int(20), int(120)),0, 5e-3 * 200, (0,255,0),2)
        cv2.putText(frame, "Current Counter: "+str(i),(int(20), int(80)),0, 5e-3 * 200, (0,255,0),2)
        cv2.putText(frame, "FPS: %f"%(fps),(int(20), int(40)),0, 5e-3 * 200, (0,255,0),3)
        # cv2.namedWindow("YOLO4_Deep_SORT", 0);
        # cv2.resizeWindow('YOLO4_Deep_SORT', 1024, 768);
        # cv2.imshow('YOLO4_Deep_SORT', frame)
        for line_to_draw in line_counter.get_lines():
            cv2.line(frame, line_to_draw[0], line_to_draw[1], (255, 0, 0), 2)

        if writeVideo_flag:
            # save a frame
            out.write(frame)
            frame_index = frame_index + 1


        fps  = ( fps + (1./(time.time()-t1)) ) / 2
        out.write(frame)
        frame_index = frame_index + 1

        # Press Q to stop!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    print(" ")
    print("[Finish]")
    end = time.time()

    #Writing the file name and vehicle count, detection time, detection fps, and encoding metadata 
    fileName = args['input'].split("/")[-1]
    fileSize = os.path.getsize(args['input'])*1e-6 #In MegaBytes
    # fnameWithoutExt = fname.split(".")[0]

    import csv
    with open('detection_log.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([fileName, vehicle_count, fileSize, (end-start_time), fps, \
            args['metadata'], args['time'], get_video_length(args['input'])])

    if len(pts[track.track_id]) != None:
       print(args["input"][43:57]+": "+ str(count) + " " + str(class_name) +' Found')

    else:
       print("[No Found]")
	#print("[INFO]: model_image_size = (960, 960)")
    video_capture.release()
    if writeVideo_flag:
        out.release()
        list_file.close()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(YOLO())
