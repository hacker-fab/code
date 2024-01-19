#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 21:14:18 2023

@author: frankzhao
"""
# dot detection and count
import cv2
import numpy as np

def detect_dot_centers(image_path):
    # Read the image
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    image = cv2.resize(image, None, fx=0.25, fy=0.25)
    # Convert the image to grayscale for circle detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow("gray",gray)
    cv2.waitKey(0)


    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(5, 5))
    cl1 = clahe.apply(gray)
    cv2.imshow("gray",cl1)
    cv2.waitKey(0)

    imgblur=cv2.GaussianBlur(cl1, (5,5), 0)
    cv2.imshow("gray",imgblur)
    cv2.waitKey(0)

    add2img=cv2.add(imgblur,imgblur)
    add3img=cv2.add(add2img,imgblur)
    cv2.imshow("gray",add3img)
    cv2.waitKey(0)

#   equalized_gray = cv2.equalizeHist(addimg)
#   cv2.imshow("gray",equalized_gray)
#   cv2.waitKey(0)
    equalized_gray=add3img

    # HoughCircles detection, parameters need be tuned
    circles = cv2.HoughCircles(equalized_gray, cv2.HOUGH_GRADIENT, dp=1, minDist=70,
                               param1=50, param2=35, minRadius=25, maxRadius=45)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(image, (x, y), r, (0, 255, 0), 2)  # Draw circle
            cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)  # Draw center of circle

        # Save the output image with detected centers
        cv2.imwrite('output.png', image)

        # display the image
        cv2.imshow("Detected Centers", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No circles were detected.")

detect_dot_centers('dot2.jpg')
