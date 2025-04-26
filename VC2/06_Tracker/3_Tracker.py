import numpy as np
import cv2
import cv2.aruco as aruco

#create your marker using http://chev.me/arucogen/
markerssize = 0.1 #in m
markertype = aruco.DICT_6X6_250

# open calibration
cv_file = cv2.FileStorage("calib.yaml", cv2.FILE_STORAGE_READ)
mtx = cv_file.getNode("camera_matrix").mat()
dist = cv_file.getNode("dist_coeff").mat()

#------------------ ARUCO TRACKER ---------------------------

# get webcam stream
cap = cv2.VideoCapture(0)

# set up ArUco
aruco_dict = aruco.Dictionary_get(markertype)
parameters = aruco.DetectorParameters_create()
parameters.adaptiveThreshConstant = 10

cv2.namedWindow("frame", cv2.WND_PROP_FULLSCREEN)
while (True):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # lists of ids and the corners belonging to each id
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    # check if the ids list is not empty
    if np.all(ids != None):

        # estimate pose of each marker and return the values
        rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, markerssize, mtx, dist)

        #draw axes
        length=0.1
        thickness=10

        for i in range(0, ids.size):
            axis = np.float32([[0,0,0],[length,0,0], [0,length,0], [0,0,length]]).reshape(-1,3)
            imgpts, jac= cv2.projectPoints(axis, rvec[i], tvec[i], mtx, dist)
            imgpts = np.int32(imgpts).reshape(-1,2)

            print("Marker "+str(ids[i][0])+" tvec: "+str(tvec[i])+" rvec: "+str(rvec[i]))

            aruco.drawDetectedMarkers(frame, corners)

            cv2.line(frame, tuple(imgpts[0].ravel()), tuple(imgpts[1].ravel()), (0, 0, 255), thickness);
            cv2.line(frame, tuple(imgpts[0].ravel()), tuple(imgpts[2].ravel()), (0, 255, 0), thickness);
            cv2.line(frame, tuple(imgpts[0].ravel()), tuple(imgpts[3].ravel()), (255, 0, 0), thickness);

            cv2.imshow('frame',frame)

        # code to show ids of the marker found
        strg = ''
        for i in range(0, ids.size):
            strg += str(ids[i][0])+' '

        cv2.putText(frame, "Id(s): " + strg, (0,64), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2,cv2.LINE_AA)

    else:
        # no markers are found
        cv2.putText(frame, "No Ids", (0,64), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2,cv2.LINE_AA)

    # display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release
cap.release()
cv2.destroyAllWindows()