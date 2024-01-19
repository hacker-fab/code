import cv2
import numpy as np
gblur=3
org = cv2.imread('etch.jpg')
org=cv2.resize(org,dsize=(1360,867), fx=1, fy=1,interpolation=cv2.INTER_LINEAR)
# Convert the image to grayscale
gray = cv2.cvtColor(org, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to the grayscale image

imGaussianMean = cv2.GaussianBlur(gray, (0, 0), gblur)


# Threshold the blurred grayscale image using OTSU's thresholding method
_, imBW = cv2.threshold(imGaussianMean, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

kernel_size = (4, 4)
# Apply erosion to remove small dots
imBW_cleaned = cv2.erode(imBW, np.ones(kernel_size, dtype=np.uint8), iterations=1)
imBW=imBW_cleaned


# Define the size of the kernel for opening (adjust as needed)
kernel_size = (15, 15)
# Apply opening to remove larger patterns
imBW_large_patterns = cv2.morphologyEx(imBW, cv2.MORPH_OPEN, np.ones(kernel_size, dtype=np.uint8))

#Substract
imBW=cv2.subtract(imBW,imBW_large_patterns)

#cv2.imshow("Result",imBW)
#cv2.waitKey(0)

# Apply skeletonization
size = np.size(imBW)
skel = np.zeros(imBW.shape, np.uint8)
element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
done = False

while not done:
    eroded = cv2.erode(imBW, element)
    temp = cv2.dilate(eroded, element)
    temp = cv2.subtract(imBW, temp)
    skel = cv2.bitwise_or(skel, temp)
    imBW = eroded.copy()

    zeros = size - cv2.countNonZero(imBW)
    if zeros == size:
        done = True


cv2.imshow("Skeleton Image", skel)
#cv2.waitKey(0)


kernel_size = (8, 8)
# Apply erosion to remove small dots
im1 = cv2.dilate(skel, np.ones(kernel_size, dtype=np.uint8), iterations=1)

cv2.imshow("dilate Image", im1)
#cv2.waitKey(0)

#ret, contours, hierarchy = cv2.findContours(im1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
contours, hierarchy = cv2.findContours(im1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

cv2.drawContours(org,contours,-1,(255,0,0),1) #blue contours
cv2.imshow("result", org)
#cv2.waitKey(0)

n=0
for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    if 35<w<60 and 35<h<60: #limit w and h
        cx=x+w//2
        cy=y+h//2
        cv2.circle(org, (cx, cy), 3, (0, 0, 255), -1) #red center point of cross
        n=n+1
        print("%d (%4d,%4d)" %(n,cx,cy))
        #1 (1153, 747)
        #2 ( 152, 691)

cv2.imshow("result", org)
cv2.waitKey(0)

cv2.destroyAllWindows()
