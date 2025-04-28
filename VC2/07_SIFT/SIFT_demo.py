# IMPOTANT: as SIFT is patetned you have to install an older version:
# pip install opencv-contrib-python==3.4.2.16

#see: https://docs.opencv.org/master/db/d27/tutorial_py_table_of_contents_feature2d.html
#especially sections: Introduction to SIFT (Scale-Invariant Feature Transform) and Feature Matching

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
img1 = cv.imread('./VC2/07_SIFT/scene.pgm',cv.IMREAD_GRAYSCALE)   # queryImage
img2 = cv.imread('./VC2/07_SIFT/book.pgm',cv.IMREAD_GRAYSCALE) # trainImage

# Initiate SIFT detector
sift = cv.SIFT_create()
# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1,None)
kp2, des2 = sift.detectAndCompute(img2,None)

# display the matches
img1M=cv.drawKeypoints(img1,kp1,img1,flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
img2M=cv.drawKeypoints(img2,kp2,img2,flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
plt.figure("Scene Keypoints")
plt.axis('off')
plt.imshow(img1M)
plt.figure("Object Keypoints")
plt.axis('off')
plt.imshow(img2M)

# BFMatcher with default params
bf = cv.BFMatcher()
matches = bf.knnMatch(des1,des2,k=2)
# Apply ratio test
good = []
for m,n in matches:
    if m.distance < 0.75*n.distance:
        good.append([m])

# cv.drawMatchesKnn expects list of lists as matches.
imgMatches = cv.drawMatchesKnn(img1,kp1,img2,kp2,good,None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
plt.figure("Matches")
plt.axis('off')
plt.imshow(imgMatches),plt.show()