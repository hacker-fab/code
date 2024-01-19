#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 19:26:39 2023

@author: frankzhao
"""

import numpy as np
import cv2 as cv
#Threshold for matching
MIN_MATCH_COUNT = 20

#img1 = cv.imread('snakesmall1.jpg',0) #180 theta
#img1 = cv.imread('aligntest.jpg',0) #0 theta
img1 = cv.imread('weird5.jpg',0) #0 theta

img1 = cv.resize(img1, None, fx=0.25, fy=0.25)
#Create test set
#tests=['aligntest2.jpg','aligntest3.jpg','aligntest4.jpg']
tests=['weird6.jpg']


    
for t in range(len(tests)):
    img2 = cv.imread(tests[t],0)
    
    #Resize image2 to match the size of image1, for test only, no need to have this in real application
    img2 = cv.resize(img2, (img1.shape[1], img1.shape[0]))

    #Initiate SIFT detector, use xfeatures2d lib only for lower version of openCV
    #sift = cv.xfeatures2d.SIFT_create()
    sift=cv.SIFT_create()
    #find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)
    
    #Store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
#       if m.distance < 0.7*n.distance:
#           good.append(m)
        good.append(m)
    if len(good)>MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
        matchesMask = mask.ravel().tolist()
        h,w = img1.shape
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2) #top-left, bottom-left, bottom-right, top-right; 4 corner points at img1
        dst = cv.perspectiveTransform(pts,M)                                  #Transform to img2 use M
        img2 = cv.polylines(img2,[np.int32(dst)],True,255,3, cv.LINE_AA)      #Draw White rectangle dst on img2
#       img2 = cv.polylines(img2,[np.int32(dst)],True,  0,3, cv.LINE_AA)      #Draw Black rectangle dst on img2

        print("t:%.2d M:%.2s" %(t,str(M))) #Print the trasition matrix.

        old=False #True for old method
        if old:
            # Extract the translation
            dx = M[0, 2]
            dy = M[1, 2]
        else:# New method
            # dx,dy is x,y offset between center of rectangle dst and center of img2
            rect_dst=np.int32(dst)
            print("rect_dst:%s" %str(rect_dst))
            h2,w2=img2.shape
            print("(rect_dst[0][0][0]+rect_dst[2][0][0])//2:%d" %((rect_dst[0][0][0]+rect_dst[2][0][0])//2))
            print("(rect_dst[0][0][1]+rect_dst[2][0][1])//2:%d" %((rect_dst[0][0][1]+rect_dst[2][0][1])//2))
            dx = w2//2 - (rect_dst[0][0][0]+rect_dst[2][0][0])//2
            dy = h2//2 - (rect_dst[0][0][1]+rect_dst[2][0][1])//2

        # Calculate theta
        theta = np.arctan2(M[1, 0], M[0, 0]) * 180 / np.pi

        # Display the displacement and rotation angle
        print(f"Displacement (dx, dy): ({dx}, {dy})")
        print(f"Rotation angle (theta): {theta} degrees")



        cv.imshow("img2",img2)
        cv.waitKey(0)
    else:
        print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
        matchesMask = None
    draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                       singlePointColor = None,
                       matchesMask = matchesMask, # draw only inliers
                       flags = 2)
    img3 = cv.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
    cv.namedWindow('image')
    cv.imshow('image',img3)
    cv.waitKey(0)
    cv.destroyAllWindows()
