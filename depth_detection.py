import numpy as np
import cv2
import sys
import max_version


if __name__ == "__main__":
    file_name = sys.argv[1]
    number = int(file_name)
    while True:

        number += 1
        frame = cv2.imread(str(number)+'.png')
        depth_image = np.load(str(number)+'.npy')
        slice1Copy = np.uint8(depth_image)
        slicecanny = cv2.Canny(slice1Copy, 0, 50, 201)
        x, y, r, led_strips = max_version.armour_detection(frame)
        print(depth_image[y][x])
        cropped_edge = slicecanny[(y-r):(y+r), (x-r):(x+r)]
        im2, contours, h = cv2.findContours(slice1Copy, 1, 2)
        cv2.drawContours(depth_image, contours, -1, (255, 255, 255), 1)
        cv2.imshow("Edges of Depth", slicecanny)
        cv2.imshow("terer", cropped_edge)
        if cv2.countNonZero(cropped_edge) < 100:
            print(number)
            cv2.circle(frame, (x, y), r, (0, 255, 0), 3)
        cv2.imshow("OUTPUT", frame)
        print(cv2.countNonZero(cropped_edge))
        input_key = cv2.waitKey(5) & 0xFF
        if input_key == 32:
            break
