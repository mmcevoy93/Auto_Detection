import numpy as np
import cv2
import sys
import math


class Armour:
    """
        This will find and store the armour based on inputted frames
    """

    def __init__(self):
        self.x = None               # x coordinate of armour
        self.y = None               # y coordinate of armour
        self.radius = None          # radius of armour
        self.width = None           # width of frame
        self.height = None          # height of frame
        self.min_led = 15           # minimum led size to look for
        self.max_led = 100          # maximum led size to look for
        self.light = None           # lighting level of frame
        self.color_frame = None     # Frame to manipulate
        self.depth_frame = None     # Depth frame to manipulate
        self.lower = None           # lower bound as tuple (B, G, R)
        self.upper = None           # upper bound as tuple (B, G, R)
        self.leds = []              # List of leds (x, y, radius)
        self.noise_level = 60       # Amount of noise on armour thats alright
        self.angle = None           # angle between two leds
        self.distance = 600         # distance of armour away from camera
        self.v1 = 0                 # canny 1
        self.v2 = 100               # canny 2
        self.v3 = 0                 # canny 3

    def _light_intensity(self, color_frame):
        """
            light level of frame

            Arguments:
                Normal frame
        """
        grey = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
        self.light = np.average(grey)

    def _set_bounds(self, color_frame):
        """
            determine upper and lower bounds for masking

            Arguments:
                Normal frame
        """
        self._light_intensity(color_frame)

        if self.light is not None:
            if self.light < 40:
                self.lower = np.array([0, 0, 150])
                self.upper = np.array([210, 255, 255])
            else:
                self.lower = np.array([0, 0, 150])
                self.upper = np.array([210, 100, 255])

    def _mask_light(self, color_frame):
        """
            Masks out the red leds

            Arguments:
                Normal frame
        """
        self._set_bounds(color_frame)
        frame_HSV = cv2.cvtColor(color_frame, cv2.COLOR_BGR2HSV)
        self.color_frame = cv2.inRange(frame_HSV, self.lower, self.upper)
        cv2.imshow("Masked", self.color_frame)

    def _led_locations(self, color_frame):
        """
            Finds all leds

            Arguments:
                Normal frame
        """
        self._mask_light(color_frame)
        ret, thresh = cv2.threshold(self.color_frame, 127, 255, 1)
        im2, contours, h = cv2.findContours(thresh, 1, 2)
        led_strips = []
        # NOTE Changed led_strips to list in this version
        for contour in contours:
            tempCircle = cv2.minAreaRect(contour)
            led_width = int(tempCircle[1][1])
            led_height = int(tempCircle[1][0])

            x = int(tempCircle[0][0])
            y = int(tempCircle[0][1])
            led_radius = (led_width+led_height)/2
            if led_radius > self.min_led or led_radius > self.max_led:
                led_strips.append((x, y, led_radius))

        self.leds = led_strips

    def _depth_slice(self, depth_frame):
        """
            initiallizes depth image for use

            Arguments:
                Depth image frame
        """
        slice1Copy = np.uint8(depth_frame)

        self.depth_frame = cv2.Canny(slice1Copy, self.v1, self.v2)
        # cv2.imshow("canny_edges", self.depth_frame)

    def _test_point(self, led1, led2):
        """
            takes two leds and finds the middle

            also finds the positive angle of those two points

            Arguments:
                tuples:
                    led1 = (x, y, radius)
                    led2 = (x, y, radius)
        """
        self.x = (led1[0]+led2[0]) / 2
        self.y = (led1[1]+led2[1]) / 2
        self.radius = min(led1[2], led2[2])
        angle = math.atan2(math.fabs(led2[1]-led1[1]),
                           math.fabs(led2[0]-led1[0]))
        self.angle = math.fabs(math.degrees(angle))
        if self.x > self.width or self.y > self.height:
            self.x = None
            self.y = None
            self.radius = None

    def _test_armour(self):
        """
            test section of possible armour

            Returns:
                True if it is Armour
                False if not Armour
        """
        y = self.y
        x = self.x
        r = self.radius

        cropped_edge = self.depth_frame[(y-r):(y+r), (x-r):(x+r)]

        if cv2.countNonZero(cropped_edge) < self.noise_level \
           and self.angle < 10:
            return True
        else:
            return False

    def _distance_away(self, depth_frame):
        """
            determines how far away armour is
            Arguments:
                Depth image frame
        """
        if self.x is not None:
            self.distance = depth_frame[self.y, self.x]
        else:
            self.distance = 600

    def _change_noise(self):
        """
            Changes the bounds of Canny

            NOTE: need to adjust for better preformance
        """
        if self.distance > 800:
            self.v1 = 10
        elif self.distance > 1000:
            self.v1 = 30
        else:
            self.v1 = 10

    def _size(self, color_frame):
        """
            simply determines the size of frame

            Arguments:
                Normal frame
        """
        self.height, self.width = color_frame.shape

    def find_armour(self, color_frame, depth_frame):
        """
            Finds the armour of robot based on rgb frame and depth frame

            Arguments:
                Normal frame
                Depth image frame
        """
        self._change_noise()
        self._depth_slice(depth_frame)
        self._led_locations(color_frame)
        self._size(depth_frame)
        is_armour = False
        led_strips = self.leds
        test_radius = led_strips[0][2]  # The led should be this size normally
        while led_strips:
            led1 = led_strips.pop(0)
            if (led1[2] < test_radius - 5) or (led1[2] > test_radius + 5):
                # if led is not around this test size then skip it
                continue
            for led2 in led_strips:
                self._test_point(led1, led2)
                is_armour = self._test_armour()
                if is_armour:
                    break
                if not is_armour:
                    self.x = None
                    self.y = None
                    self.radius = None
            if is_armour:
                break
        self._distance_away(depth_frame)

    def cirlce_leds(self, color_frame):
        """
            If needed will cirlce all leds.
            NOTE Not working properly atm

            Arguments:
                Normal frame
        """
        if self.leds is not None:
            for led in self.leds:
                cv2.circle(color_frame, (led[0], led[1]),
                           led[2], (255, 255, 255), 1)
        return color_frame


if __name__ == "__main__":
    file_name = sys.argv[1]
    number = int(file_name)
    R = Armour()
    while True:
        number += 1
        frame = cv2.imread(str(number)+'.png')
        depth_image = np.load(str(number)+'.npy')
        R.find_armour(frame, depth_image)
        if R.x is not None:
            cv2.circle(frame, (R.x, R.y), R.radius, (0, 255, 0), 2)
        cv2.imshow("Class Test", frame)
        input_key = cv2.waitKey(5) & 0xFF
        if input_key == 32:
            break
