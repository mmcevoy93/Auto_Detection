'''
    This is the code we will implement to our robot to detect the armour and
    later send this info to other parts of the code
'''
import numpy as np
import cv2
import sys

if __name__ == "__main__":

    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([110, 255, 255])
    file_name = sys.argv[1]
    frame = cv2.imread(file_name)
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    frame_mask = cv2.inRange(frame_HSV, lower_blue, upper_blue)

    frame_applied = cv2.bitwise_and(frame, frame, mask=frame_mask)

    ret, thresh = cv2.threshold(frame_mask, 127, 255, 1)
    im2, contours, h = cv2.findContours(thresh, 1, 2)

    # display our input and output images to compare
    cv2.imshow('Input Image', frame)
    cv2.imshow('Output Image', frame_applied)
    cv2.moveWindow('Input image', 1, 0)
    cv2.moveWindow('Output Image', 650, 0)

    cv2.waitKey(0)
