=== CAMERA CALIBRATION AND MARKER BASED TRACKING ===

Work through a typical marker based tracking pipeline and document your 
  - Steps,
  - Results, and 
  - Insights
in a report (“Laborbericht”) using
  - Text
  - Code fragments (if applicable), and 
  - Screenshots!

The report, including figures (screenshots, etc.), might be around 2-4 pages (A4 format). Keep it short and to the point! Please upload the report as PDF file when done. Please do not upload any additional files, everything should be in the report!

Almost all code is provided. First, make yourself familiar with the code (most parts should be rather self-explaining; for some parts you might need to look into the documentation -- i.e., google it!). Feel free to modify and/ or add some additional code to perform more detailed experiments and gain additional insights! 


(1) get some images from your webcam
File: 1_Calibration_GrabImages.py & camera-calibration-checker-board_9x7.pdf
Task: Print out the checkerboard pattern (provided) and grab some images from different viewpoints. How many images do you need? Make sure to cover a variety of different viewpoints…

(2) calibrate your camera  
File: 2_Calibration.py
Needs: Images from (1)
Task: Calibrate your camera by running the code. Interpret your camera calibration matrix -- do they make sense? How does it change when adding more or less images? Etc.

(3) run a marker based tracker 
File: 3_Tracker.py
Needs: Internal camera calibration from (2)
Task: Print out one or multiple  ArUco Marker(s) (you might use http://chev.me/arucogen/ to generate proper ones). Take care of specifying the right dictionary and marker size! Let the program estimate the marker id & pose with respect to your camera. **Play around with it!** Try to understand what's going on and ask yourself questions, such as: When does it work, what are limitations? Failure Cases? Can more than one marker be detected at the same time? What if you change (mess up) your calibration file by hand, i.e., multiplying the focal length by 10? Etc...

HAVE FUN!