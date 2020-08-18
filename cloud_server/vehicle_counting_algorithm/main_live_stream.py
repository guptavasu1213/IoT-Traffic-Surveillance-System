from __future__ import division, print_function, absolute_import

import os
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

# Line counter method
from counter import *


# PURPOSE: Displaying the FPS of the detected video
# PARAMETERS: Start time of the frame, number of frames within the same second
# RETURN: New start time, new number of frames
def displayFPS(start_time, num_frames):
    current_time = int(time.time())
    time_elapsed = current_time - start_time
    if (current_time > start_time):
        fps = num_frames / time_elapsed
        print("FPS:", fps)


pts = [deque(maxlen=30) for _ in range(9999)]
warnings.filterwarnings('ignore')

# initialize a list of colors to represent each possible class label
np.random.seed(100)
COLORS = np.random.randint(0, 255, size=(200, 3),
                           dtype="uint8")

# Path to the vehicle counting algorithm folder
PATH_TO_FOLDER = "vehicle_counting_algorithm"

max_cosine_distance = 0.3
nn_budget = None
nms_max_overlap = 1.0

counter = []
# deep_sort
model_filename = os.path.join(PATH_TO_FOLDER, 'model_data/market1501.pb')
encoder = gdet.create_box_encoder(model_filename, batch_size=1)

metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
tracker = Tracker(metric)


vehicle_count = None
line_counter = None
count_file_path = None

yolo = YOLO(PATH_TO_FOLDER)

def initialize_vars(coordinates, path, currentResolution):
    '''

    '''
    global line_counter, count_file_path, vehicle_count
    vehicle_count = 0
    line_counter = Counter(coordinates, currentResolution)
    count_file_path = path
def write_count():
    global vehicle_count
    # Writing to a log file
    with open(count_file_path, 'a') as file:
        file.write(str(vehicle_count)+"\n")
    vehicle_count = 0 #Reset count

import time

def main(video_file_path):
    video_capture = cv2.VideoCapture(video_file_path)

    fps = 0.0

    global vehicle_count
    global num_frames

    num_frames = 0

    total_frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
    # Initializing the progress bar
    pbar = tqdm(total=total_frames)

    # main loop
    while num_frames < total_frames:
        num_frames += 1
        ret, frame = video_capture.read()  # frame shape 640*480*3

        if ret != True:
            break
        t1 = time.time()

        image = Image.fromarray(frame[..., ::-1])  # bgr to rgb
        boxs, confidence, class_names = yolo.detect_image(image)
        features = encoder(frame, boxs)
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
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 255, 255), 2)

        for track in tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue

            indexIDs.append(int(track.track_id))
            counter.append(int(track.track_id))
            bbox = track.to_tlbr()
            color = [int(c) for c in COLORS[indexIDs[i] % len(COLORS)]]

            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (color), 3)
            b0 = str(bbox[0])  # .split('.')[0] + '.' + str(bbox[0]).split('.')[0][:1]
            b1 = str(bbox[1])  # .split('.')[0] + '.' + str(bbox[1]).split('.')[0][:1]
            b2 = str(bbox[2] - bbox[0])  # .split('.')[0] + '.' + str(bbox[3]).split('.')[0][:1]
            b3 = str(bbox[3] - bbox[1])

            cv2.putText(frame, str(track.track_id), (int(bbox[0]), int(bbox[1] - 50)), 0, 5e-3 * 150, (color), 2)
            if len(class_names) > 0:
                class_name = class_names[0]
                cv2.putText(frame, str(class_names[0]), (int(bbox[0]), int(bbox[1] - 20)), 0, 5e-3 * 150, (color), 2)

            i += 1
            center = (int(((bbox[0]) + (bbox[2])) / 2), int(((bbox[1]) + (bbox[3])) / 2))

            pts[track.track_id].append(center)

            thickness = 5
            # center point
            cv2.circle(frame, (center), 1, color, thickness)

            # If the box intersects with the line
            if line_counter.intersects_with_bbox(bbox) and track.track_id not in line_counter.trackedID:
                line_counter.addToTrackedList(track.track_id)
                vehicle_count += 1

            # draw motion path
            for j in range(1, len(pts[track.track_id])):
                if pts[track.track_id][j - 1] is None or pts[track.track_id][j] is None:
                    continue
                thickness = int(np.sqrt(64 / float(j + 1)) * 2)
                cv2.line(frame, (pts[track.track_id][j - 1]), (pts[track.track_id][j]), (color), thickness)

        count = len(set(counter))
        cv2.putText(frame, "Total Line Counter: " + str(vehicle_count), (int(20), int(120)), 0, 5e-3 * 200, (0, 255, 0),
                    2)
        cv2.putText(frame, "FPS: %f" % (fps), (int(20), int(40)), 0, 5e-3 * 200, (0, 255, 0), 3)

        for line_to_draw in line_counter.get_lines():
            cv2.line(frame, line_to_draw[0], line_to_draw[1], (255, 0, 0), 2)

        fps = (fps + (1. / (time.time() - t1))) / 2

        pbar.update(1)

        # Press Q to stop!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    pbar.close()
    print("[Finish]")

    if len(pts[track.track_id]) != None:
        print(str(vehicle_count) + ' vehicles found')
    else:
        print("[No Found]")

    video_capture.release()
    cv2.destroyAllWindows()