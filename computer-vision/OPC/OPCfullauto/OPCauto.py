#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 12:59:55 2023

@author: zhaoyanzhi
"""
import cv2
import numpy as np

def apply_opc_correction(image_path, output_path, radius=2, stroke_thickness=1, erosion_iterations=1):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)    
    # OPC Step 1 Erode the image to make the gate pattern slightly thinner
    kernel = np.zeros((3,3), np.uint8)
    img = cv2.erode(img, kernel, iterations=erosion_iterations)

    # Harris corner detection
    dst = cv2.cornerHarris(img, 2, 3, 0.04)
    dst = cv2.dilate(dst, None)
    # Get corner cordinates
    corner_xy = np.argwhere(dst > 0.01 * dst.max())

    # OPC Step 2 Corners
    for loc in corner_xy:
        cv2.circle(img, tuple(reversed(loc)), radius, 255, stroke_thickness)
    # Save corrected image
    cv2.imwrite(output_path, img)
    # Display the corrected image(not necessary, just for test)
    #cv2.imshow('OPC Corrected', img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

# A simple test
image_path = "NMOSNOR.jpg"
output_path = "OPC_corrected.jpg"
apply_opc_correction(image_path, output_path, radius=1,stroke_thickness=1,erosion_iterations=1)

