# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 09:35:30 2017

@author: TWang

Height Analysis 2.0 

update: add pedestrain box ratio range, clear some boxes near to camera

reference paper: Pedestrian Detection: An Evaluation of the State of the Art

the mean pedestrian box w/h aspect ratio is 0.41 

we adopt that range is 0.35-0.45

"""

import numpy as np
import cv2
import time
import os

        
video_name = r"D:\Pedestrian Detection\test_video\fix_3.mp4"
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
        '''
        remove other pedestrain box, just leave full body box using aspect ratio
        '''
        # get x, y coordeiante from detections
        box_coordinate = detections[:,[1,2,3,4]]
        box_coordinate = (box_coordinate * np.array([w, h, w, h])).astype("int")

        #get each pedestrian box aspect ratio, convert (N,) to (N,1)
        aspect_ratio = (box_coordinate[:,2]-box_coordinate[:,0]) / (box_coordinate[:,3]-box_coordinate[:,1])
        New_aspect_ratio = aspect_ratio.reshape((aspect_ratio.size,1))

        #define aspect ratio range 
        aspect_ratio_range_lower = 0.35 
        aspect_ratio_range_upper = 0.45 
        
        #add New_aspect_ratio column to box_coordinate, (N * 5)
        New_box_coordinate = np.append(box_coordinate,New_aspect_ratio, axis = 1)
        
        Final_box_coordinate_list = []

        for idx, val in enumerate(New_box_coordinate):
            
            # if aspect ratio in range(0.35,0.45), processing and ddraw reference plane
            if aspect_ratio_range_lower < val[4] < aspect_ratio_range_upper:
                
                #create a new box coordinate abd convert from list to array
                Final_box_coordinate_list.append(New_box_coordinate[idx])
                Final_box_coordinate_array = np.array(Final_box_coordinate_list)
                
                # get new box x,y corrdinate
                Final_Height_Analysis_range = Final_box_coordinate_array[:,[1,3]]
                Final_Width_Analysis_range = Final_box_coordinate_array[:,[0,2]]
                
                #calculate height and width range
                Final_Height_range = Final_box_coordinate_array[:,3]-Final_box_coordinate_array[:,1]
                Final_Width_range = Final_box_coordinate_array[:,2]-Final_box_coordinate_array[:,0]

                #sort height and return medium one
                Height_median = np.median(Final_box_coordinate_array[:,3]-Final_box_coordinate_array[:,1])
                Height_mean = np.mean(Final_box_coordinate_array[:,3]-Final_box_coordinate_array[:,1])
                
                #get median and mean index 
                median_index = np.nanargmin(np.abs(Final_Height_range-Height_median))
                mean_index = np.nanargmin(np.abs(Final_Height_range-Height_mean))
                
                #from indxe, find its coordinate
                median_index_y1 = Final_Height_Analysis_range[median_index][0]
                median_index_y2 = Final_Height_Analysis_range[median_index][1]
        
                mean_index_y1 = Final_Height_Analysis_range[mean_index][0]
                mean_index_y2 = Final_Height_Analysis_range[mean_index][1] 
        
                #define reference plane scale factor
                reference_plane_scale = 0.2
                
                #drawing a retangular reference plane
                cv2.rectangle(frame, (0, int(median_index_y1*(1-reference_plane_scale))), (w, int(median_index_y2*(1+reference_plane_scale))),(211,211,211), 2)
                
                #define height cale factor
                height_scale = 0.2
    
    
    
                for det in detections:
                    #get probability of each box
                    confidence = det[0]
                    
                    #bounding box real coordinate
                    box = det[1:] * np.array([w, h, w, h])
                    
                    #float to int
                    (x1, y1, x2, y2) = box.astype("int")
                    
                    #person probabiity 
                    label = "person:%.2f"%(confidence * 100.0)
                    
                    #draw a box
                    cv2.rectangle(frame, (x1, y1), (x2, y2),COLORS, 2)
                    
                    #draw class label probality 
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
            
    #calculate fps    
    toc = time.time()
    durr = float(toc-tic)
    fps = 1.0 / durr
    cv2.putText(frame,"fps:%.3f"%fps,(20,20),3,1.0,(0,0,255),2,cv2.LINE_AA)
    
    cv2.imshow("Frame",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


#==============================================================================
#                 New_box_coordinate_reshape = New_box_coordinate[idx].reshape((New_box_coordinate[idx].size,1))
#                
#                 New_box_coordinate_reshape_T = New_box_coordinate_reshape.T
#                 
#                 results.append(New_box_coordinate_reshape_T)
#==============================================================================
                
               
                
#==============================================================================
#                 New_box_coordinate_reshape = New_box_coordinate[idx].reshape((New_box_coordinate[idx].size,1))
#                 
#                 New_box_coordinate_reshape_T = New_box_coordinate_reshape.T
#                 
#                 result = np.vstack([result,New_box_coordinate_reshape_T])
#==============================================================================