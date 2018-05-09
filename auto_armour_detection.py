import numpy as np
import cv2
import sys
import math

class Armour:
    """
        This will find and store the armour based on inputted frames
    """

    def __init__(self):
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.radius = None
        self.min_led = 10
        self.max_led = 100
        self.light = None
        self.color_frame = None
        self.depth_frame = None
        self.lower = None
        self.upper = None
        self.leds = None
        self.noise_level = 40
        self.angle = None
        self.distance = None
        self.v1 = 0
        self.v2 = 30
        self.v3 = 200

    def _light_intensity(self, color_frame):
        """
            light level of frame
        """
        grey = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
        self.light = np.average(grey)

    def _set_bounds(self, color_frame):
        """
            determine upper and lower bounds for masking
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
        """
        self._set_bounds(color_frame)
        frame_HSV = cv2.cvtColor(color_frame, cv2.COLOR_BGR2HSV)
        self.color_frame = cv2.inRange(frame_HSV, self.lower, self.upper)
        cv2.imshow("Masked", self.color_frame)

    def _led_locations(self, color_frame):
        """
            Finds all leds
        """
        self._mask_light(color_frame)
        ret, thresh = cv2.threshold(self.color_frame, 127, 255, 1)
        im2, contours, h = cv2.findContours(thresh, 1, 2)
        led_strips = []
        # NOTE Changed led_strips to list
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
        """
        slice1Copy = np.uint8(depth_frame)
        self.depth_frame = cv2.Canny(slice1Copy, self.v1, self.v2, self.v3)
        cv2.imshow("edges", self.depth_frame)

    def find_armour(self, color_frame, depth_frame):
        """
            Finds the armour of robot based on rgb frame and depth frame
        """
        self._change_noise()
        self._depth_slice(depth_frame)
        self._led_locations(color_frame)
        self._size(depth_frame)
        is_armour = False
        led_strips = self.leds
        while led_strips:
            led1 = led_strips.pop(0)
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

    def _test_point(self, led1, led2):
        """
            takes two leds and finds the middle

            also finds the positive angle of those two points
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
        if self.x is not None:
            self.distance = depth_frame[self.y, self.x]
        else:
            self.distance = 800

    def _change_noise(self):
        if self.distance > 700:
            self.v2 = 100
        else:
            self.v2 = 30

    def cirlce_leds(self, color_frame):
        if self.leds is not None:
            for led in self.leds:
                cv2.circle(color_frame, (led[0], led[1]),
                           led[2], (255, 255, 255), 1)
        return color_frame

    def _size(self, color_frame):
        self.height, self.width = color_frame.shape


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

        # frame = R.cirlce_leds(frame)

        cv2.imshow("Class Test", frame)
        input_key = cv2.waitKey(5) & 0xFF
        if input_key == 32:
            break
