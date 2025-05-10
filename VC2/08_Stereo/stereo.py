import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

ply_header = '''ply
format ascii 1.0
element vertex %(vert_num)d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
'''
def write_ply(fn, verts, colors):
    verts = verts.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    verts = np.hstack([verts, colors])
    with open(fn, 'wb') as f:
        f.write((ply_header % dict(vert_num=len(verts))).encode('utf-8'))
        np.savetxt(f, verts, fmt='%f %f %f %d %d %d ')

# use your own images and/or use some prerecorded stereo pairs:
# http://vision.middlebury.edu/stereo/data/
imgL = cv.imread('tsukuba_l.png',0)
imgR = cv.imread('tsukuba_r.png',0)

#adjust numDisparity and blockSize for your images!
stereo = cv.StereoBM_create(numDisparities=64, blockSize=15)

print('computing disparity...')
disp = stereo.compute(imgL,imgR)

print('generating 3d point cloud...',)
h, w = imgL.shape[:2]
f = 0.8*w                          # guess for focal length
Q = np.float32([[1, 0, 0, -0.5*w],
                [0,-1, 0,  0.5*h], # turn points 180 deg around x-axis,
                [0, 0, 0,     -f], # so that y-axis looks up
                [0, 0, 1,      0]])
points = cv.reprojectImageTo3D(disp, Q)
colors = cv.cvtColor(imgL, cv.COLOR_GRAY2RGB)
mask = disp > disp.min()+16
out_points = points[mask]
out_colors = colors[mask]
out_fn = 'out.ply'
write_ply(out_fn, out_points, out_colors)
print('%s saved -- open e.g. with MeshLab' % out_fn)

plt.imshow(disp,'gray')
plt.show()