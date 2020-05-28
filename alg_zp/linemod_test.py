import os
import sys
import cv2
import numpy as np


img = cv2.imread('./image/1585532459.6078084.jpg')

template = cv2.imread('./image/5.jpg')
h, w = template.shape[:2]
mask = np.zeros(template.shape)

mask[5:50, 2:32] = 255

# detector = cv2.linemod.getDefaultLINEMOD()
detector = cv2.linemod.getDefaultLINE()
detector.addTemplate(template, '5', mask)

# a = detector.match(img, 60)
detector.numClasses()