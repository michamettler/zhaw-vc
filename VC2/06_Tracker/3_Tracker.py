import numpy as np
import cv2
import cv2.aruco as aruco

# Marker Setup
markersize = 0.1  # Markergröße in Meter
markertype = aruco.DICT_6X6_250

# Kamera laden
cv_file = cv2.FileStorage("calib.yaml", cv2.FILE_STORAGE_READ)
mtx = cv_file.getNode("camera_matrix").mat()
mtx[0,0] *= 10  # f_x
mtx[1,1] *= 10  # f_y
dist = cv_file.getNode("dist_coeff").mat()

# ArUco Dictionary und Detector
aruco_dict = aruco.getPredefinedDictionary(markertype)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

# Video
cap = cv2.VideoCapture(0)

# 3D Koordinaten der Marker-Ecken (im Marker-Referenzsystem)
objPoints = np.array([
    [-0.5,  0.5, 0],
    [ 0.5,  0.5, 0],
    [ 0.5, -0.5, 0],
    [-0.5, -0.5, 0]
]) * markersize

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is not None:
        aruco.drawDetectedMarkers(frame, corners, ids)

        for i in range(len(ids)):
            # solvePnP erwartet genau diese Inputs
            retval, rvec, tvec = cv2.solvePnP(objPoints, corners[i][0], mtx, dist)

            if retval:
                # Achse zeichnen
                cv2.drawFrameAxes(frame, mtx, dist, rvec, tvec, 0.05)
                print(f"Marker {ids[i][0]} -> tvec: {tvec.ravel()}, rvec: {rvec.ravel()}")

    else:
        cv2.putText(frame, "No Ids", (0, 64), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
