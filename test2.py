import cv2
import os
import sys

TARGET_FILE = sys.argv[1]
IMG_DIR = os.path.abspath(os.path.dirname(__file__)) + '/images/'

target_img = cv2.imread(target_img_path)
target_hist = cv2.calcHist([target_img], [0], None, [256], [0, 256])

comparing_img_path = sys.argv[2]
comparing_img = cv2.imread(comparing_img_path)
comparing_hist = cv2.calcHist([comparing_img], [0], None, [256], [0, 256])

ret = cv2.compareHist(target_hist, comparing_hist, 0)

print(ret)
