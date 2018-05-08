# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 09:57:58 2017

@author: Walton TWang

Height Analysis 1.0 

"""

import imutils
import numpy as np
import cv2
import time
import os



"""
model address:
    https://github.com/chuanqi305/MobileNet-SSD
    trained on COCO and fine-tuned at PASCAL dataset,mAP = 0.72
    
related links:
    https://github.com/Zehaos/MobileNet
    https://www.pyimagesearch.com/2017/09/11/object-detection-with-deep-learning-and-opencv/
"""


video_name = r"street_1.mp4"
root_dir = r"D:\Pedestrian Detection\dnn_detector"

proto = root_dir + "\\MobileNetSSD_deploy.prototxt.txt"
mobile_ssd = root_dir + "\\MobileNetSSD_deploy.caffemodel"


CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

COLORS = (0,255,0)

confidence_threshold = 0.2

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(proto,mobile_ssd)
    
cap = cv2.VideoCapture(video_name)


while cap.isOpened():
    
    tic = time.time()
    ret,frame = cap.read()
    if not ret:
        break
    
    #get frame size, h = 720, w = 1080
    (h, w) = frame.shape[:2]
    
    #input blob for the image by resizing to a fixed 300x300 pixels and then normalizing it
    # (note: normalization is done via the authors of the MobileNet SSD implementation)
    blob = cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)),0.007843,size=(300,300),mean=127.5)
    
    # pass the blob through the network and obtain the detections and predictions
    print("[INFO] computing object detections...")
    net.setInput(blob)
    detections = net.forward() # size is 1*1*N*7 [0,class_index,probability,x1, y1, x2, y2]
    
    detections = detections[0,0,:] # size is N*7 [0,class_index,probability,x1, y1, x2, y2]

    #select detecions in person and confidence_threshold > 0.2 , return detections # size is N*5 [probability,x1, y1, x2, y2]
    detections = np.asarray([det[2:] for det in detections if int(det[1]) == CLASSES.index('person') and det[2] > confidence_threshold])
    
    
    '''height pedestrain analysis part'''
    if detections.size > 0:
        #get y coordinate from detections
        Height_Analysis_range = detections[:,[2,4]]*h
        Height_Analysis_range = Height_Analysis_range.astype("int")
        
        #get each bounding box height
        Height_range = Height_Analysis_range[:,1] - Height_Analysis_range[:,0]
        
        #sort them 
        Height_median = np.median(Height_range)
        Height_mean = np.mean(Height_range)
        
        #get median and mean index 
        median_index = np.nanargmin(np.abs(Height_range-Height_median))
        mean_index = np.nanargmin(np.abs(Height_range-Height_mean))
        
        #convert to reference box coordinate
        median_index_y1 = Height_Analysis_range[median_index][0]
        median_index_y2 = Height_Analysis_range[median_index][1]

        mean_index_y1 = Height_Analysis_range[mean_index][0]
        mean_index_y2 = Height_Analysis_range[mean_index][1] 

        #define reference threshold scale factor
        reference_plane_scale = 0.2
        
        #drawing a reference box
        cv2.rectangle(frame, (0, int(median_index_y1*(1-reference_plane_scale))), (w, int(median_index_y2*(1+reference_plane_scale))),(211,211,211), 2)
        
        #define height cale factor
        height_scale = 0.2
        
        for det in detections:
            confidence = det[0]
    
            box = det[1:] * np.array([w, h, w, h])
            (x1, y1, x2, y2) = box.astype("int")
            
            label = "person:%.2f"%(confidence * 100.0)
            cv2.rectangle(frame, (x1, y1), (x2, y2),COLORS, 2)
            y = y1 - 15 if y1 - 15 > 15 else y1 + 15
            cv2.putText(frame,label,(x1,y),cv2.FONT_HERSHEY_SIMPLEX,0.5,COLORS,2)
            
            '''determine Short / Medium / High'''
            if y2 - y1 < int(median_index_y1*(1 + 2 * reference_plane_scale)):
                
                if y2 - y1 > Height_median * (1 + height_scale ):
                    Height_label = "High"
                    cv2.putText(frame,Height_label,(x1,y1+30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(211,211,211),2)
                    
                if Height_median * (1 - height_scale ) < y2 - y1 < Height_median * (1 + height_scale ):
                    Height_label = "Medium"
                    cv2.putText(frame,Height_label,(x1,y1+30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(211,211,211),2)
                
                if Height_median * (1 - height_scale ) > y2 - y1 :
                    Height_label = "Short"
                    cv2.putText(frame,Height_label,(x1,y1+30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(211,211,211),2)
                
        
    toc = time.time()
    durr = float(toc-tic)
    fps = 1.0 / durr
    cv2.putText(frame,"fps:%.3f"%fps,(20,20),3,1.0,(0,0,255),2,cv2.LINE_AA)
    cv2.imshow("Frame",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

    







