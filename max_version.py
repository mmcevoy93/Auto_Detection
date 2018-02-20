'''
    This is the code we will implement to our robot to detect the armour and
    later send this info to other parts of the code
'''
import numpy as np
import cv2
import sys


def set_low_up(Lighting="Bright"):
    '''
        This function will decide the best lower and uppper ranges bounds
        for masking

        Inputs:
            Lighting levels

        Outputs:
            upper and lower arrays

    '''
    # TODO add more bounds and figure out what lighting works best
    if Lighting == "Dark":
        # if lighting is super dark
        # NOTE light_intensity > 20
        lower = np.array([100, 30, 50])
        upper = np.array([130, 255, 255])
    if Lighting == "Bright":
        lower = np.array([100, 0, 0])
        upper = np.array([200, 20, 255])

    return lower, upper


def light_intensity(frame):
    '''
        This function determines the light level of frame
        I will use this to determine what to set the upper and lower bounds
        of our masking function

        Inputs:
            the orignal frame
        Outputs:
            number from 0 - 255 based on the light level in frame
                -if smaller than frame is darker
                -if larger than frame is brighter
    '''
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    light_level = np.average(grey)
    return light_level


if __name__ == "__main__":

    file_name = sys.argv[1]
    frame = cv2.imread(file_name)
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower, upper = set_low_up("Dark")
    frame_mask = cv2.inRange(frame_HSV, lower, upper)

    frame_applied = cv2.bitwise_and(frame, frame, mask=frame_mask)
    print(light_intensity(frame))
    ret, thresh = cv2.threshold(frame_mask, 127, 255, 1)
    im2, contours, h = cv2.findContours(thresh, 1, 2)
    cv2.drawContours(frame, contours, -1, (0, 0, 255), 1)

    for contour in contours:
        tempCircle = cv2.minAreaRect(contour)
        width = int(tempCircle[1][1])
        height = int(tempCircle[1][0])
        x = int(tempCircle[0][0])
        y = int(tempCircle[0][1])
        # NOTE Truely what we need to work with is the x and y parts.
        # Later we maybe use width and height to isolate the meaningful leds
        cv2.circle(frame, (x, y), (width+height)/2,
                          (255, 255, 0), 1)

    cv2.imshow('Input Image', frame)            # displays our input and
    cv2.imshow('Output Image', frame_applied)   # output images to compare
    cv2.moveWindow('Input image', 0, 0)
    cv2.moveWindow('Output Image', 650, 0)

    cv2.waitKey(0)
