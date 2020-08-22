from __future__ import division, print_function, absolute_import
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input",help="path to input video", required=True)
ap.add_argument("-lc", "--lineCoordinates",help="line coordinates (separated by ';' for multiple lines);\
				\"x1,y1,x2,y2; x1,y1,x2,y2\"", required=True)
ap.add_argument("-fp", "--folderPath", help="Path to the detection algorithm folder. Only pass this flag if running "
											"this file outside the folder", required=False, default="")
# ap.add_argument("-r", "--resolutionRatio",help="only pass if trying different resolutions: \
# 	video resolution ratio = current resolution/original resolution; Pass 'WidthRatioxHeightRatio'", required=False, default='1x1')
ap.add_argument("-cf", "--CountFilePath",help="count file path", required=False, default="count_log/")

args = vars(ap.parse_args())

resolution = [1920, 1080] #############SWITCH IT

import sys
import os
import datetime
from timeit import time
import warnings
import cv2
import numpy as np
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

from tqdm import tqdm

#Line counter method
from counter import *

# PURPOSE: Displaying the FPS of the detected video
# PARAMETERS: Start time of the frame, number of frames within the same second
# RETURN: New start time, new number of frames 
def displayFPS(start_time, num_frames):
	current_time = int(time.time())
	time_elapsed = current_time - start_time
	if(current_time > start_time):
		fps  = num_frames/time_elapsed
		print("FPS:", fps)

pts = [deque(maxlen=30) for _ in range(9999)]
warnings.filterwarnings('ignore')

# initialize a list of colors to represent each possible class label
np.random.seed(100)
COLORS = np.random.randint(0, 255, size=(200, 3),
	dtype="uint8")

#Path to the vehicle counting algorithm folder
PATH_TO_FOLDER = args["folderPath"]

def main(yolo):

	start = time.time()
	max_cosine_distance = 0.3
	nn_budget = None
	nms_max_overlap = 1.0

	counter = []
	#deep_sort
	model_filename = os.path.join(PATH_TO_FOLDER, 'model_data/market1501.pb')
	encoder = gdet.create_box_encoder(model_filename,batch_size=1)

	metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
	tracker = Tracker(metric)


	print("========>", args["input"])
	writeVideo_flag = True
	video_capture = cv2.VideoCapture(args["input"])
	fps = video_capture.get(cv2.CAP_PROP_FPS)


	if writeVideo_flag:
	# Define the codec and create VideoWriter object
		w = int(video_capture.get(3))
		h = int(video_capture.get(4))
		fourcc = cv2.VideoWriter_fourcc(*'MJPG')
		out = cv2.VideoWriter('./output/output.avi', fourcc, fps, (w, h))
		frame_index = -1

	fps = 0.0
	start_time = int(time.time())
	num_frames = 0
	vehicle_count = 0

	# Line intersection counter
	line_counter = Counter(args['lineCoordinates'], resolution)
	total_frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)

	#Initializing the progress bar
	pbar = tqdm(total=total_frames)

	# main loop
	while num_frames < total_frames:
		# os.system('clear')
		num_frames+= 1
		# print("Current Frame:\t", str(num_frames) + '/' + str())
		#Calculating fps each second
		# displayFPS(start_time, num_frames)

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

		for track in tracker.tracks:
			if not track.is_confirmed() or track.time_since_update > 1:
				continue

			indexIDs.append(int(track.track_id))
			counter.append(int(track.track_id))
			bbox = track.to_tlbr()
			color = [int(c) for c in COLORS[indexIDs[i] % len(COLORS)]]

			cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])),(color), 3)
			b0 = str(bbox[0])#.split('.')[0] + '.' + str(bbox[0]).split('.')[0][:1]
			b1 = str(bbox[1])#.split('.')[0] + '.' + str(bbox[1]).split('.')[0][:1]
			b2 = str(bbox[2]-bbox[0])#.split('.')[0] + '.' + str(bbox[3]).split('.')[0][:1]
			b3 = str(bbox[3]-bbox[1])

			cv2.putText(frame,str(track.track_id),(int(bbox[0]), int(bbox[1] -50)),0, 5e-3 * 150, (color),2)
			if len(class_names) > 0:
			   class_name = class_names[0]
			   cv2.putText(frame, str(class_names[0]),(int(bbox[0]), int(bbox[1] -20)),0, 5e-3 * 150, (color),2)

			i += 1
			center = (int(((bbox[0])+(bbox[2]))/2),int(((bbox[1])+(bbox[3]))/2))

			pts[track.track_id].append(center)

			thickness = 5
			#center point
			cv2.circle(frame, (center), 1, color, thickness)

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
		cv2.putText(frame, "FPS: %f"%(fps),(int(20), int(40)),0, 5e-3 * 200, (0,255,0),3)

		for line_to_draw in line_counter.get_lines():
			cv2.line(frame, line_to_draw[0], line_to_draw[1], (255, 0, 0), 2)

		if writeVideo_flag:
			# save a frame
			out.write(frame)
			# frame_index = frame_index + input_filepath


		fps  = ( fps + (1./(time.time()-t1)) ) / 2
		# out.write(frame)
		# frame_index = frame_index + 1

		pbar.update(1)


		# Press Q to stop!
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	pbar.close()
	print("[Finish]")
	end = time.time()
	
	fileName = args['input'].split("/")[-1].split(".")[0] #without extension

	# #Writing to a log file
	# with open(args['CountFilePath'], 'w') as file:
	# 	file.write(str(vehicle_count))

	if len(pts[track.track_id]) != None:
	   print(args["input"][43:57]+": "+ str(vehicle_count) + ' vehicles found')

	else:
	   print("[No Found]")
	video_capture.release()
	if writeVideo_flag:
		out.release()
	cv2.destroyAllWindows()

if __name__ == '__main__':
	main(YOLO(PATH_TO_FOLDER))
