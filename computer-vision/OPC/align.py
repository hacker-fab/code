#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 19:26:39 2023

@author: zhaoyanzhi
"""

import cv2
import numpy as np

# Load images
image1 = cv2.imread('snake.jpg', cv2.IMREAD_GRAYSCALE)
image2 = cv2.imread('snaketest.jpg', cv2.IMREAD_GRAYSCALE)

# Resize image2 to match the size of image1
image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

# Detect and extract key points and descriptors using ORB
orb = cv2.ORB_create()
keypoints1, descriptors1 = orb.detectAndCompute(image1, None)
keypoints2, descriptors2 = orb.detectAndCompute(image2, None)

# Create a Brute Force Matcher
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Match descriptors
matches = bf.match(descriptors1, descriptors2)

# Sort the matches by distance (shortest distance first)
matches = sorted(matches, key=lambda x: x.distance)

# Keep only the top N matches (you can adjust this threshold as needed)
N = 10
good_matches = matches[:N]

# Extract the matching keypoints
src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

# Calculate the transformation matrix using RANSAC
M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

# Extract the translation
dx = M[0, 2]
dy = M[1, 2]

# Calculate the rotation angle (theta)
theta = np.arctan2(M[1, 0], M[0, 0]) * 180 / np.pi

# Apply non-maximum suppression (NMS) to keypoints
def non_max_suppression(keypoints, min_distance):
    selected_indices = []
    
    for i, kp1 in enumerate(keypoints):
        keep = True
        for j, kp2 in enumerate(keypoints):
            if i != j and np.linalg.norm(np.array(kp1.pt) - np.array(kp2.pt)) < min_distance:
                keep = False
                break
        if keep:
            selected_indices.append(i)
    
    return [keypoints[i] for i in selected_indices]

# Set the minimum distance threshold for non-maximum suppression (NMS)
min_distance = 2

# Apply non-maximum suppression (NMS) to keypoints
keypoints1 = non_max_suppression(keypoints1, min_distance)
keypoints2 = non_max_suppression(keypoints2, min_distance)

# Draw feature points on both images with numbers
image1_with_keypoints = cv2.drawKeypoints(image1, keypoints1, None, color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
image2_with_keypoints = cv2.drawKeypoints(image2, keypoints2, None, color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# Draw numbers on the keypoints
for i, kp in enumerate(keypoints1):
    x, y = kp.pt
    cv2.putText(image1_with_keypoints, str(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

for i, kp in enumerate(keypoints2):
    x, y = kp.pt
    cv2.putText(image2_with_keypoints, str(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

# Draw matches between keypoints1 and keypoints2
#matching_image = cv2.drawMatches(image1, keypoints1, image2, keypoints2, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

# Show the images with feature points and matching lines
cv2.imshow('Image 1 with Numbered Keypoints', image1_with_keypoints)
cv2.imshow('Image 2 with Numbered Keypoints', image2_with_keypoints)
#cv2.imshow('Matching Points', matching_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Display the displacement and rotation angle
print(f"Displacement (dx, dy): ({dx}, {dy})")
print(f"Rotation angle (theta): {theta} degrees")


