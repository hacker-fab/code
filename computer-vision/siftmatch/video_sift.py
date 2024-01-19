#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 19:42:34 2023

@author: zhaoyanzhi
"""

import cv2 as cv
import numpy as np
import time

# Threshold for matching
MIN_MATCH_COUNT = 20
# Scale Factor
scale=1
# Open video file
cap = cv.VideoCapture('cvtest_short.mp4')

# Check if video opened successfully
if not cap.isOpened():
    print("Error opening video file")

# Read the first frame
ret, img1 = cap.read()

# Initialize odometry display
mapsize=1000
odometry_image = np.zeros((mapsize, mapsize, 3), np.uint8)
last_location = (int(mapsize/2), int(mapsize/2))  # Start pos.
cv.circle(odometry_image, (int(mapsize/2),int(mapsize/2)), 5, (255, 255, 255), -1)
if ret:
    img1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
    img1 = cv.resize(img1, None, fx=scale, fy=scale)

    # Initialize SIFT detector
    sift = cv.SIFT_create()

    # Process each frame
    while True:
        ret, img2 = cap.read()
        if not ret:
            break
        start_time = time.time()
        img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
        img2 = cv.resize(img2, (img1.shape[1], img1.shape[0]))
        cv.imshow("input video",img2)
        # Find keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)

        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 50)
        flann = cv.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)

        # Store all the good matches as per Lowe's ratio test
        good = []
        for m, n in matches:
            good.append(m)

        if len(good) > MIN_MATCH_COUNT:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
            h, w = img1.shape
            pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
            dst = cv.perspectiveTransform(pts, M)
            #img2 = cv.polylines(img2, [np.int32(dst)], True, 255, 3, cv.LINE_AA)

            rect_dst = np.int32(dst)
            h2, w2 = img2.shape
            dx = w2//2 - (rect_dst[0][0][0] + rect_dst[2][0][0]) // 2
            dy = h2//2 - (rect_dst[0][0][1] + rect_dst[2][0][1]) // 2

            # Calculate theta
            theta = np.arctan2(M[1, 0], M[0, 0]) * 180 / np.pi

            # Update odometry
            new_location = int(mapsize/2)+int(dx), int(mapsize/2)+int(dy) #always compare to frame 1
            if ((new_location[0]-last_location[0])**2+(new_location[1]-last_location[1])**2)<300*16:
                cv.line(odometry_image, last_location, new_location, (0, 255, 0), 1)
                last_location = new_location
                cv.circle(odometry_image, new_location, 1, (0, 0, 255), -1)
    
            
            # new_location = (last_location[0]+int(dx), last_location[1]+int(dy)) #compares to last valid frame        
            # if ((new_location[0]-last_location[0])**2+(new_location[1]-last_location[1])**2)<100:
            #     cv.line(odometry_image, (last_location[0]+int(mapsize/2),last_location[1]+int(mapsize/2)), (new_location[0]+int(mapsize/2),new_location[1]+int(mapsize/2)), (0, 255, 0), 1)
            #     last_location = new_location
            #     img1=img2
            #     cv.circle(odometry_image, (new_location[0]+int(mapsize/2),new_location[1]+int(mapsize/2)), 1, (0, 0, 255), -1)
            

            # Display the displacement and rotation angle for each frame
            print(f"Frame {cap.get(cv.CAP_PROP_POS_FRAMES)}: Displacement (dx, dy): ({dx}, {dy}), Rotation angle (theta): {theta} degrees")

        else:
            print("Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT))

        elapsed_time = time.time() - start_time
        print(f"Time taken to process frame: {elapsed_time:.2f} seconds")

        # Display the displacement odometry
        cv.imshow("Displacement Odometry", odometry_image)

        if cv.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
            break

# Release the video capture object and close windows
cap.release()
cv.destroyAllWindows()
