'''
    This is the code we will implement to our robot to detect the armour and
    later send this info to other parts of the code
'''
import numpy as np
import cv2
import sys
import math

def set_low_up(Lighting):
    '''
        This function will decide the best lower and uppper ranges bounds
        for masking

        Inputs:
            Lighting levels

        Outputs:
            upper and lower arrays

    '''
    # TODO add more bounds and figure out what lighting works best
    # seems to get everything but i'll keep if's incase something changes
    lower = np.array([50, 0, 255])
    upper = np.array([220, 255, 255])

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


def detect_armour(led_strips):

    return


if __name__ == "__main__":

    file_name = sys.argv[1]
    frame = cv2.imread(file_name)
    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    print(light_intensity(frame))
    lighting = light_intensity(frame)
    lower, upper = set_low_up(lighting)
    frame_mask = cv2.inRange(frame_HSV, lower, upper)

    frame_applied = cv2.bitwise_and(frame, frame, mask=frame_mask)

    ret, thresh = cv2.threshold(frame_mask, 127, 255, 1)
    im2, contours, h = cv2.findContours(thresh, 1, 2)
    cv2.drawContours(frame, contours, -1, (0, 0, 255), 1)

    led_strips = {}
    count = 0
    for contour in contours:
        tempCircle = cv2.minAreaRect(contour)
        led_width = int(tempCircle[1][1])
        led_height = int(tempCircle[1][0])
        x = int(tempCircle[0][0])
        y = int(tempCircle[0][1])
        led_radius = (led_width+led_height)/2
        if led_width > led_height:
            cv2.circle(frame, (x, y), led_radius,
                              (255, 255, 0), 1)
            led_strips[count] = [x, y, led_radius]
            count += 1
    if count-1 in led_strips:
        # last values not needed in dictionary. It is boarder
        del led_strips[count-1]
    print(led_strips)

    cv2.imshow('Input Image', frame)            # displays our input and
    cv2.imshow('Output Image', frame_applied)   # output images to compare
    cv2.moveWindow('Input image', 0, 0)
    cv2.moveWindow('Output Image', 650, 0)

    cv2.waitKey(0)
