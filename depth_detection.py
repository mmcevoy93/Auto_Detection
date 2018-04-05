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
        slicecanny = cv2.Canny(slice1Copy, 0, 200)


        # cv2.imshow("Depth Image", depth_image)
        # cv2.imshow("Input", frame)
        # cv2.moveWindow("Input", 0, 0)


        x, y, r = max_version.armour_detection(frame)

        sub_edge = slicecanny[(y-r):(y+r), (x-r):(x+r)]

        im2, contours, h = cv2.findContours(slice1Copy, 1, 2)
        cv2.drawContours(depth_image, contours, -1, (255, 255, 255), 1)
        # cv2.imshow("Contous of Depth", frame)
        # cv2.moveWindow("Contours of Depth", 600, 0)

        # cv2.circle(slicecanny, (x, y), r, (255, 0, 0), 3)

        cv2.imshow("Edges of Depth", slicecanny)
        # cv2.moveWindow("Edges of Depth", 600, 0)
        # cv2.imshow("Cut", sub_edge)
        if cv2.countNonZero(sub_edge) == 0:
            print(number)
            cv2.circle(frame, (x, y), r, (255, 0, 127), 3)
        cv2.imshow("number", frame)

        input_key = cv2.waitKey(5) & 0xFF

        if input_key == 32:
            break
