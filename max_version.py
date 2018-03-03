'''
    This is the code we will implement to our robot to detect the armour and
    later send this info to other parts of the code
'''
import numpy as np
import cv2
import sys


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


def draw_circles(frame, leds):
    '''
        Getting rid of unneeded led points picked up
        Specifically if two circles interect that they are too close to have
        armour inside it

        Sometimes will remove important circles

        Input:
            frame and x, y and radius values in a dictionary

        Output:
            No return just draws led circles

    '''
    # TODO Work this to be better

    for o in leds:
        x = leds[o][0]
        y = leds[o][1]
        radius = leds[o][2]
        cv2.circle(frame, (x, y), radius,
                          (255, 255, 0), 1)


def find_armour(frame, led_strips):
    '''
        Finds the armour plates on robots

        Inputs:
            Dictionary of leds
                keys are 0 - n leds found
                values are (x, y, r)
                    x is x coordinate
                    y is y coordinate
                    r is led_radius
        Outputs:
            no output at the moment
            will adjust this later
            for now draws the pink circle where it thinks armour is
    '''

    radius = []
    for n in led_strips:
        radius.append(led_strips[n][2])
    average_radius = sum(radius)/len(radius)

    remove = []
    for n in led_strips:
        if led_strips[n][2] < average_radius:
            remove.append(n)
        pass
    for r in remove:
        if r in led_strips:
            del led_strips[r]
    new = {}
    count = 0
    for n in led_strips:
        new[count] = led_strips[n]
        count += 1
    if len(new) > 1:
        x = (list(new[0])[0] + list(new[1])[0]) / 2
        y = (list(new[0])[1] + list(new[1])[1]) / 2
        armour_radius = list(new[0])[2]
        cv2.circle(frame, (x, y), armour_radius,
                          (205, 0, 230), 3)

    return


def armour_detection(frame):
    '''
        Main function of program
        manipulates frames to be able to find armour

        Input:
            frame you wish to detect armour on

        Output:
            returns nothing just shows a window of frame being proccessed

    '''

    frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lighting = light_intensity(frame)
    lower, upper = set_low_up(lighting)
    frame_mask = cv2.inRange(frame_HSV, lower, upper)
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

    if count-1 in led_strips:
        del led_strips[count-1]
    # possible that nothing will be detected this will catch that
    if len(led_strips) > 2:
        draw_circles(frame, led_strips)  # NOTE will not be needed in final ver
        find_armour(frame, led_strips)
    cv2.imshow('Input Image', frame)            # displays our input and
    cv2.moveWindow('Input image', 0, 0)

    cv2.waitKey(5)

if __name__ == "__main__":

    file_name = sys.argv[1]
    frame = cv2.imread(file_name)
    armour_detection(frame)
