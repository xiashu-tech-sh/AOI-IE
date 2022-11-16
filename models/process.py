import cv2 as cv2
import os
import numpy as np
import imghdr

image_dir = 'test2'
result_dir = 'output'

steps = [
    '01_equalize',
    '02_contrast',
    '03_threshold',
    '04_dilate',
    '05_contour',
]


# Create directories
if not os.path.exists(result_dir):
    os.mkdir(result_dir)

for step in steps:
    dirpath = os.path.join(result_dir, step)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)


if __name__ == '__main__':

    for file in os.listdir(image_dir):
        filepath = os.path.join(image_dir, file)
        if imghdr.what(filepath):

            img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

            # equalized_img = cv2.equalizeHist(img)
            # cv2.imwrite(os.path.join(result_dir, steps[0], file[:-4] + '1.jpg'), equalized_img)

            threshold = cv2.threshold(img, 22, 255, cv2.THRESH_BINARY_INV)[1]           
            cv2.imwrite(os.path.join(result_dir, steps[2], file[:-4] + '2.jpg'), threshold)

            kernel = np.ones((5,5),np.uint8)
            opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)

            cv2.imwrite(os.path.join(result_dir, steps[3], file[:-4] + '3.jpg'), opening)

            _, contours, hierarchy  = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contoured = cv2.cvtColor(opening, cv2.COLOR_GRAY2RGB)
            for i, contour in enumerate(contours):
                if hierarchy[0][i][3] == -1:
                    area = cv2.contourArea(contour)
                    if 7000 < area < 15000:
                        contoured = cv2.drawContours(
                            contoured, [contour], 0, (100, 100, 255), 2)
            cv2.imwrite(os.path.join(result_dir, steps[4], file[:-4] + '4.jpg'), contoured)

