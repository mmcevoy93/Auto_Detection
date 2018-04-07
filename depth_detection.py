import numpy as np
import cv2
import sys
import max_version


def mag_thresh(image, sobel_kernel=3, mag_thresh=(0, 255)):
    # Calculate gradient magnitude
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Take both Sobel x and y gradients
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=sobel_kernel)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=sobel_kernel)
    # Calculate the gradient magnitude
    gradmag = np.sqrt(sobelx**2 + sobely**2)
    # Rescale to 8 bit
    scale_factor = np.max(gradmag)/255
    gradmag = (gradmag/scale_factor).astype(np.uint8)
    # Create a binary image of ones where threshold is met, zeros otherwise
    binary_output = np.zeros_like(gradmag)
    binary_output[(gradmag >= mag_thresh[0]) & (gradmag <= mag_thresh[1])] = 1

    # Return the binary image
    return binary_output


if __name__ == "__main__":
    file_name = sys.argv[1]
    number = int(file_name)
    while True:

        number += 1
        frame = cv2.imread(str(number)+'.png')
        depth_image = np.load(str(number)+'.npy')
        slice1Copy = np.uint8(depth_image)

        slicecanny = cv2.Canny(slice1Copy, 0, 125, 101)
        # slicecanny = mag_thresh(slice1Copy)
        # cv2.imshow("Depth Image", depth_image)
        # cv2.imshow("Input", frame)
        # cv2.moveWindow("Input", 0, 0)

        x, y, r = max_version.armour_detection(frame)
        print(depth_image[y][x])
        sub_edge = slicecanny[(y-r):(y+r), (x-r):(x+r)]

        im2, contours, h = cv2.findContours(slice1Copy, 1, 2)
        cv2.drawContours(depth_image, contours, -1, (255, 255, 255), 1)
        # cv2.imshow("Contous of Depth", frame)
        # cv2.moveWindow("Contours of Depth", 600, 0)

        # cv2.circle(slicecanny, (x, y), r, (255, 0, 0), 3)

        cv2.imshow("Edges of Depth", slicecanny)
        # cv2.moveWindow("Edges of Depth", 600, 0)
        # cv2.imshow("Cut", sub_edge)
        if cv2.countNonZero(sub_edge) < 100:
            print(number)
            cv2.circle(frame, (x, y), r, (0, 255, 0), 3)
        cv2.imshow("OUTPUT", frame)
        print(cv2.countNonZero(sub_edge))

        input_key = cv2.waitKey(5) & 0xFF

        if input_key == 32:
            break
