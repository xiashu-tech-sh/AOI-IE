# import the necessary packages
from skimage.measure import compare_ssim  as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
import os

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err
 
def compare_images(imageA, imageB ):
	# compute the mean squared error and structural similarity
	# index for the images
	imageA[imageA>30] = 255
	imageA[imageA<30] = 0
	imageB[imageB>30] = 255
	imageB[imageB<30] = 0

	if imageA.shape != imageB.shape:
		if( imageA.shape[0] == imageB.shape[1] and
		 	imageA.shape[1] == imageB.shape[0] ):
			M = cv2.getRotationMatrix2D((imageB.shape[0]/2,imageB.shape[1]/2),90,1)
			imageB = cv2.warpAffine(imageB,M,(imageB.shape[0],imageB.shape[1]))
		else:
			print( "Size different")
			return([0,0])
		
	m = mse(imageA, imageB)
	s = ssim(imageA, imageB)
	print('m', m, 's', s)
	return([m,s])
	# setup the figure
	# fig = plt.figure(title)
	# plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))
 
	# # show first image
	# ax = fig.add_subplot(1, 2, 1)
	# plt.imshow(imageA, cmap = plt.cm.gray)
	# plt.axis("off")
 
	# # show the second image
	# ax = fig.add_subplot(1, 2, 2)
	# plt.imshow(imageB, cmap = plt.cm.gray)
	# plt.axis("off")
 
	# # show the images
	# plt.show()

big_path = './test'
to_delete = []
for dir in os.listdir(big_path):
	okpath = big_path+'/'+dir + '/OK'
	okfiles = os.listdir(okpath)
	ngpath = big_path+'/'+dir + '/NG'
	std = cv2.imread( okpath + '/' + okfiles[0], cv2.IMREAD_GRAYSCALE )
	for file in okfiles[1:]:
		im2 = cv2.imread( okpath + '/' + file, cv2.IMREAD_GRAYSCALE )
		print(okpath + '/' + file)
		compare_images(std, im2 )
	for file in os.listdir(ngpath):
		im2 = cv2.imread( ngpath + '/' + file, cv2.IMREAD_GRAYSCALE )
		print(ngpath + '/' + file)
		compare_images(std, im2 )

		# if (file != '.DS_Store'):
		# 	print(file)
		# 	img = cv2.imread( path + '/' + file, cv2.IMREAD_GRAYSCALE )
		# 	img[img>50] = 255
		# 	img[img<50] = 0
		# 	cv2.imshow("test", img)
		# 	h, w = img.shape
		# 	if h%2:
		# 		im1 = img[:int(h/2)]
		# 		im2 = img[int(h/2)+1:]
		# 	else:
		# 		im1 = img[:int(h/2)]
		# 		im2 = img[int(h/2):]

		# 	im2 = np.flip(im2, axis = 0)
		# 	cv2.imshow("im1", im1)
		# 	cv2.imshow("im2", im2)
		# 	# cv2.waitKey(0)
		# 	compare_images(im1, im2 )