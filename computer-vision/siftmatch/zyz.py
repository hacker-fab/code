#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 19:26:39 2023

@author: frankzhao
"""

import cv2
import numpy as np

# Load images
image1 = cv2.imread('snakesmall1.jpg', cv2.IMREAD_GRAYSCALE)
image2 = cv2.imread('snaketest.jpg', cv2.IMREAD_GRAYSCALE)

# Resize image2 to match the size of image1, for test only, no need to have this in real application
image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

# Detect and extract key points
orb = cv2.ORB_create()
keypoints1, descriptors1 = orb.detectAndCompute(image1, None)
keypoints2, descriptors2 = orb.detectAndCompute(image2, None)

# Create a matcher (Brute Force)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Match feature points
matches = bf.match(descriptors1, descriptors2)

# Sort the matches by distance (shortest distance first)
# TODO: Optimize the match region by region
matches = sorted(matches, key=lambda x: x.distance)

# Keep only the top N matches (ideally 3 is ok, but for testing I used 10 instead)
N = 10
good_matches = matches[:N]

# Extract the matching feature points
src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

# Calculate the transformation matrix using RANSAC
M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

# Extract the translation
dx = M[0, 2]
dy = M[1, 2]

# Calculate theta
theta = np.arctan2(M[1, 0], M[0, 0]) * 180 / np.pi

# Draw feature points on both images
image1_with_keypoints = cv2.drawKeypoints(image1, keypoints1, None, color=(0, 255, 0), flags=0)
image2_with_keypoints = cv2.drawKeypoints(image2, keypoints2, None, color=(0, 255, 0), flags=0)

# Draw lines between matching points pairs
matching_image = cv2.drawMatches(image1, keypoints1, image2, keypoints2, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

# Show the images with feature points and matching lines
cv2.imshow('Image 1 with Keypoints', image1_with_keypoints)
cv2.imshow('Image 2 with Keypoints', image2_with_keypoints)
cv2.imshow('Matching Points', matching_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Display the displacement and rotation angle
print(f"Displacement (dx, dy): ({dx}, {dy})")
print(f"Rotation angle (theta): {theta} degrees")
