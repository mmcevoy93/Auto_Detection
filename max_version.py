'''
    This is the code we will implement to our robot to detect the armour and
    later send this info to other parts of the code
'''
import numpy as np
import cv2
import sys
import math


def set_low_up(lighting, led_color='Red'):
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
    if led_color == 'Blue':
        lower = np.array([50, 0, 255])
        upper = np.array([220, 255, 255])
    if (led_color == 'Red') and (lighting < 40):
        # lighting level 25
        lower = np.array([0, 0, 150])
        upper = np.array([210, 255, 255])
    if (led_color == 'Red') and (lighting > 40):
        lower = np.array([0, 0, 150])
        upper = np.array([210, 100, 255])
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


def inside_circles(leds):
    '''
        Getting rid of unneeded led points picked up
        Specifically if two circles interect that they are too close to have
        armour inside it

        Sometimes will remove important circles

        Input:
            dictionary of leds x, y, z values

        Output:
            same dictionary but removing unneeded points

    '''
    # TODO Work this to be better
    to_remove = []
    if count-1 in led_strips:
        del led_strips[count-1]
    for n in leds:
        for m in leds:
            dx = abs(leds[m][0]-leds[n][0])
            dy = abs(leds[m][1]-leds[n][1])
            Rn = leds[n][2]
            Rm = leds[m][2]
            if n == m:
                continue
            if (math.sqrt(math.pow(dx, 2) + math.pow(dy, 2)) < (Rn+Rm)) and (math.sqrt(math.pow(dx, 2) + math.pow(dy, 2)) > math.fabs(Rn-Rm)):
                to_remove.append(n)
                to_remove.append(m)
    for r in to_remove:
        if r in leds:
            del leds[r]
    for o in leds:
        x = leds[o][0]
        y = leds[o][1]
        radius = leds[o][2]
        cv2.circle(frame, (x, y), radius,
                          (255, 255, 0), 1)

    return leds


def detect_armour(led_strips):

    # gonna try size first.
    led_1 = 1
    led_2 = 0
    for n in led_strips:
        for m in led_strips:
            if n == m:
                continue
            if abs(led_strips[n][1] - led_strips[m][1]) < abs(led_strips[led_1][1] - led_strips[led_2][1]):
                led_1 = n
                led_2 = m
    x = (list(led_strips[led_1])[0] + list(led_strips[led_2])[0]) / 2
    y = (list(led_strips[led_1])[1] + list(led_strips[led_2])[1]) / 2
    armour_radius = list(led_strips[led_1])[2]
    cv2.circle(frame, (x, y), armour_radius,
                      (205, 0, 230), 3)

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
        led_strips[count] = [x, y, led_radius]
        count += 1
    led_strips = inside_circles(led_strips)
    if len(led_strips) > 2:
        detect_armour(led_strips)
    print(led_strips)
    cv2.imshow('Input Image', frame)            # displays our input and
    cv2.imshow('Output Image', frame_applied)   # output images to compare
    cv2.moveWindow('Input image', 0, 0)
    cv2.moveWindow('Output Image', 650, 0)

    cv2.waitKey(0)
