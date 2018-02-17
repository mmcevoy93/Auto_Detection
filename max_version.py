'''
    This is the code we will implement to our robot to detect the armour and
    later send this info to other parts of the code
'''
import numpy as np
import cv2
import sys


def set_low_up(Lighting):

    if Lighting == "Dark":
        lower = np.array([100, 30, 50])
        upper = np.array([130, 255, 255])
    if Lighting == "Bright":
        lower = np.array([100, 0, 0])
        upper = np.array([200, 20, 255])


    return lower, upper


if __name__ == "__main__":


    file_name = sys.argv[1]
    frame = cv2.imread(file_name)
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower, upper = set_low_up("Dark")
    frame_mask = cv2.inRange(frame_HSV, lower, upper)

    frame_applied = cv2.bitwise_and(frame, frame, mask=frame_mask)

    ret, thresh = cv2.threshold(frame_mask, 127, 255, 1)
    im2, contours, h = cv2.findContours(thresh, 1, 2)

    # display our input and output images to compare
    cv2.imshow('Input Image', frame)
    cv2.imshow('Output Image', frame_applied)
    cv2.moveWindow('Input image', 0, 0)
    cv2.moveWindow('Output Image', 650, 0)

    cv2.waitKey(0)
