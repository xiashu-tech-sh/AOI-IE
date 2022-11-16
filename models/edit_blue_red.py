import numpy as np
import cv2
import os
import random
from math import sin,cos
import imutils


def get_consecutive_trues( arr ):
	result = []
	tmp_start = 0
	tmp_end = 0
	for i in range(len(arr)):
		if (i == 0 and arr[i]) or (arr[i] > arr[i-1]):
			tmp_start = i
		elif (i == len(arr)-1 and arr[i]) or (arr[i] < arr[i-1]):
			tmp_end = i
			result.append([tmp_start, tmp_end])
	return result

lower_blue = np.array([100, 120, 46])
upper_blue = np.array([124, 255, 255])
lower_red = np.array([0, 100, 100])
upper_red = np.array([25, 255, 255])
lower_green = np.array([35, 43, 46])
upper_green = np.array([77, 255, 255])

orig_path = './original'
result_path = './result'
tmp_file_num = 0
for file in os.listdir(orig_path):
	im2 = cv2.imread( orig_path + '/' + file )
	print(orig_path + '/' + file)
	cv2.imshow("origin",im2)

	# Rotate entire image
	# rows,cols,trash = im2.shape
	# print("rows", rows, "cols", cols)
	# degree = 20#random.randint(0,90)
	# M = cv2.getRotationMatrix2D((cols/2,rows/2),degree,1)
	# dst = cv2.warpAffine(im2,M,(cols,rows))
	# cv2.imshow("rotate_90",dst)
	
	hsvImg = cv2.cvtColor(im2, cv2.COLOR_BGR2HSV)

	mask_blue = cv2.inRange(hsvImg, lower_blue, upper_blue)
	open_blue = cv2.morphologyEx(
			mask_blue, cv2.MORPH_OPEN,
			cv2.getStructuringElement(
				cv2.MORPH_ELLIPSE, (3, 3)))
	
	mask_red = cv2.inRange(hsvImg, lower_red, upper_red)
	open_red = cv2.morphologyEx(
			mask_red, cv2.MORPH_OPEN,
			cv2.getStructuringElement(
				cv2.MORPH_ELLIPSE, (3, 3)))

	mask_green = cv2.inRange(hsvImg, lower_green, upper_green)
	open_green = cv2.morphologyEx(
			mask_green, cv2.MORPH_OPEN,
			cv2.getStructuringElement(
				cv2.MORPH_ELLIPSE, (3, 3)))

	res_red = cv2.bitwise_and(im2,im2,mask = open_red)
	res_red = res_red[:,:,0]
	res_green = cv2.bitwise_and(im2,im2,mask = open_green)
	res_green = res_green[:,:,1]
	res_blue = cv2.bitwise_and(im2,im2,mask = open_blue)
	res_blue = res_blue[:,:,2]

	# result_img = ((res_red/6+res_green/3+res_blue/2)*6).astype(np.uint8)
	# cv2.imshow("res_red",res_red)
	# cv2.imshow("result_img",result_img)
	
	masks_added = open_red+open_blue+open_green
	blurred_mask = cv2.GaussianBlur(masks_added, (5, 5), 1)
	v = np.median(blurred_mask)

	lower_find_mask = int(max(0, 0.5*v))
	print("lower_find_mask", lower_find_mask)
	upper_find_mask = int(min(255, 1.5 * v))
	print("upper_find_mask", upper_find_mask)
	edged_mask = cv2.Canny(blurred_mask, lower_find_mask, upper_find_mask)
	cnts_find_screen = cv2.findContours(edged_mask.copy(), cv2.RETR_LIST,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts_find_screen = cnts_find_screen[0] if imutils.is_cv2() else cnts_find_screen[1]
	rows, cols, trash = im2.shape
	handian_mask = np.zeros((rows, cols), np.uint8)
	for cnt in cnts_find_screen:
		(x, y, w, h) = cv2.boundingRect(cnt)
		if( w<5 or h <5):
			continue
		handian_mask[ int(y-0.05*h):int(y+1.05*h), int(x-0.05*w):int(x+1.05*w) ] = 255
	res = cv2.bitwise_and(im2,im2,mask = handian_mask)
	cv2.imshow("res",res)
	cv2.imwrite(result_path + '/' + file, res)
	# cv2.imshow("masks_added",masks_added)
	# horizontal_num_white_pts = [ np.sum(x) for x in masks_added ]
	# hist = np.histogram(horizontal_num_white_pts, len(horizontal_num_white_pts))
	# avg_white_points = sum(horizontal_num_white_pts)/len(horizontal_num_white_pts)
	# avg_white_points = avg_white_points/10
	# horizontal_white_lines = [ True if x > avg_white_points else False for x in horizontal_num_white_pts ]
	# consec_trues = get_consecutive_trues(horizontal_white_lines)
	# print(consec_trues)

	# for consec_true in consec_trues:
	# 	if(consec_true[1]-consec_true[0]) > im2.shape[0]/20:
	# 		roi = im2[consec_true[0]:consec_true[1], :]
	# 		# cv2.imshow("%d"%tmp_file_num,roi)
	# 		roi_row, roi_col,trash = roi.shape
	# 		# M = cv2.getRotationMatrix2D((roi_col/2,roi_row/2),45,1)
	# 		# dst = cv2.warpAffine(im2,M,(roi_col,roi_row))
	# 		# cv2.imshow("rotate_45_%d"%tmp_file_num,dst)
	# 		im2[consec_true[0]:consec_true[1], :] = 0
	# 		tmp_file_num += 1
	cv2.waitKey(0)
	cv2.destroyAllWindows()
