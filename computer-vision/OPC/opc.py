import cv2
import numpy as np

source_image = cv2.imread('snaketest.jpg')
destination_image = cv2.imread('snake.jpg')

source_points = []
destination_points = []
cv2.startWindowThread()

def mouse_callback(event, x, y, flags, param):
    global source_points, destination_points

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(source_points) < 4:
            source_points.append((x, y))
            cv2.circle(source_image, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow('Source Image', source_image)

    if event == cv2.EVENT_RBUTTONDOWN:
        if len(destination_points) < 4:
            destination_points.append((x, y))
            cv2.circle(destination_image, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow('Destination Image', destination_image)

    if len(source_points) == 4 and len(destination_points) == 4:
        transformation_matrix = cv2.getPerspectiveTransform(np.array(source_points, dtype=np.float32),
                                                           np.array(destination_points, dtype=np.float32))
        aligned_image = cv2.warpPerspective(source_image, transformation_matrix,
                                            (destination_image.shape[1], destination_image.shape[0]))
        result = cv2.addWeighted(destination_image, 0.5, aligned_image, 0.5, 0)
        cv2.imshow('Aligned Image', result)
        cv2.imwrite("res.jpg",aligned_image)

cv2.imshow('Source Image', source_image)
cv2.imshow('Destination Image', destination_image)
cv2.setMouseCallback('Source Image', mouse_callback)
cv2.setMouseCallback('Destination Image', mouse_callback)

cv2.waitKey(0)
cv2.destroyAllWindows()


