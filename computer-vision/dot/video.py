#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 12:58:43 2023

@author: frankzhao
"""

import cv2
import numpy as np
import time

def processimg(src):
    global clahe
    cl1 = clahe.apply(src)
    imgblur=cv2.GaussianBlur(cl1, (5,5), 0)
    add2img=cv2.add(imgblur,imgblur)
    result=cv2.add(add2img,imgblur)
    return result

clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(5, 5))
video_path = "231101164516.mp4"
edge_threshold = 70 #TODO adjust this, or maybe using new method for img preprocessing and circle detection.

# Load video
cap = cv2.VideoCapture(video_path)
ret, prev_frame = cap.read()

# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('output.avi', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (int(cap.get(3) * 0.25), int(cap.get(4) * 0.25)))


# clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
# prev_gray = clahe.apply(cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY))
prev_frame = cv2.resize(prev_frame, None, fx=0.25, fy=0.25)
gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
pedimg = processimg(gray)
counts = {"left": 0, "right": 0, "top": 0, "bottom": 0}

while True:
    start_time = time.time()

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, None, fx=0.25, fy=0.25)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    pedimg = processimg(gray)
    circles = cv2.HoughCircles(pedimg, cv2.HOUGH_GRADIENT, dp=1, minDist=70,
                               param1=50, param2=35, minRadius=25, maxRadius=45)#TODO this parameters need to be tuned

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            # Draw the circle in the output frame
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)

            # Draw a rectangle to mark the center of the circle
            cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

            if x < edge_threshold:
                counts["left"  ] += 1
            elif x > (frame.shape[1] - edge_threshold):
                counts["right" ] += 1
            elif y < edge_threshold:
                counts["top"   ] += 1
            elif y > (frame.shape[0] - edge_threshold):
                counts["bottom"] += 1

    # Display dot counts on the frame
    cv2.putText(frame, f"  Left: {counts['left']}"  , (10,  25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f" Right: {counts['right']}" , (10,  50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"   Top: {counts['top']}"   , (10,  75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Bottom: {counts['bottom']}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Calculate and display FPS
    end_time = time.time()
    fps = 1 / (end_time - start_time)
    cv2.putText(frame, f"FPS: {fps:.2f}", (frame.shape[1] - 100, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Video", frame)
    # cv2.waitKey(0)
    out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
