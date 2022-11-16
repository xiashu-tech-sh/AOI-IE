import os
import numpy as np
import cv2


# 源文件夹
root_dir = "./test2"
print(root_dir)
# 生成文件夹 = root_dir + '_get_handian'
target_dir = root_dir + '_get_handian'
red_dir = root_dir + '_get_handian_red'
green_dir = root_dir + '_get_handian_green'
blue_dir = root_dir + '_get_handian_blue'
if not os.path.isdir(target_dir):
    os.mkdir(target_dir)
if not os.path.isdir(red_dir):
    os.mkdir(red_dir)
if not os.path.isdir(green_dir):
    os.mkdir(green_dir)
if not os.path.isdir(blue_dir):
    os.mkdir(blue_dir)

lower_blue = np.array([100, 120, 46])
upper_blue = np.array([124, 255, 255])
lower_red = np.array([0, 100, 100])
upper_red = np.array([25, 255, 255])
lower_green = np.array([35, 43, 46])
upper_green = np.array([77, 255, 255])


# srcImg = cv2.imread(r'C:\temp\handian\source\C4_0_7_0 (6).jpg')

def get_handian_function(srcImg):
    hsvImg = cv2.cvtColor(srcImg, cv2.COLOR_BGR2HSV)

    # get blue mask
    mask_blue = cv2.inRange(hsvImg, lower_blue, upper_blue)
    open_blue = cv2.morphologyEx(
            mask_blue, cv2.MORPH_OPEN,
            cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (3, 3)))
    cv2.imwrite(mask_blue, os.path.join(blue_dir, srcImg))

    # get red mask
    mask_red = cv2.inRange(hsvImg, lower_red, upper_red)
    open_red = cv2.morphologyEx(
            mask_red, cv2.MORPH_OPEN,
            cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (3, 3)))
    cv2.imwrite(mask_red, os.path.join(red_dir, srcImg))

    # 并集
    kernel = np.ones((7,7), np.uint8)
    merge = cv2.add(open_blue, open_red)
    merge_dilate = cv2.dilate(merge, kernel)
    merge_dilate = cv2.dilate(merge_dilate, kernel)
    merge_dilate = cv2.dilate(merge_dilate, kernel)
    # cv2.imshow('merge_dilate', merge_dilate)
    # cv2.waitKey(0)

    # image, contours, hierarchy = cv2.findContours(merge_dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    image, contours, hierarchy = cv2.findContours(merge_dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for i in range(0, len(contours)):
        # print(contours[i].size)
        if contours[i].size < 80:
            continue
        x, y, w, h = cv2.boundingRect(contours[i]) 
        re = cv2.rectangle(srcImg, (x,y), (x+w,y+h), (0,255,0), 3)
    return srcImg

# 切割
# for i in range(0, len(contours)):
#     print(contours[i].size)
#     if contours[i].size < 80:
#         continue
#     x, y, w, h = cv2.boundingRect(contours[i])
#     newimage = srcImg[y+2:y+h-2,x+2:x+w-2] # 先用y确定高，再用x确定宽
#     # nrootdir=("E:/cut_image/")
#     # if not os.path.isdir(nrootdir):
#     #     os.makedirs(nrootdir)
#     # cv2.imwrite(str(i)+".jpg",newimage)
#     cv2.imshow('newimage', newimage)
#     cv2.waitKey(0)

# target = cv2.bitwise_and(srcImg, srcImg, mask=merge_dilate)
# cv2.imshow('target', target)
# cv2.waitKey(0)


if __name__ == '__main__':
    for f in os.listdir(root_dir):
        filename = os.path.join(root_dir, f)
        print(filename)
        if not os.path.isfile(filename):
            continue
        src = cv2.imread(filename)
        dst = get_handian_function(src)
        newfilename = os.path.join(target_dir, f)
        cv2.imwrite(newfilename, dst)
        print(newfilename)