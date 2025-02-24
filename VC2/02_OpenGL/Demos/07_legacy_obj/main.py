#!/usr/bin/python
# LEGACY OpenGL SAMPLE: LOAD OBJ FILE USING DISPLAY LIST

import sys
import numpy as np
from OpenGL.GLUT import *
from OpenGL.GL import *
from obj_loader import *
import os

spin = 0.0
obj_mesh = None

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    glRotatef(spin, 0.0, 1.0, 0.0)
    glTranslatef(0, -5.0, 0.0)
    glScalef(40.0, 40.0, 40.0)
    mat = [0.9, 0.8, 0.0, 0]
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, mat)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, mat)
    global obj_mesh
    glCallList(obj_mesh.gl_list)
    glPopMatrix()
    glFlush ()
    glutSwapBuffers()

def spinDisplay():
    global spin
    spin = spin + 0.025
    if (spin > 360.0):
        spin = spin - 360.0
    glutPostRedisplay()

def init():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glShadeModel(GL_SMOOTH)
    light_ambient =  [0.2, 0.2, 0.2, 1.0]
    light_diffuse =  [1.0, 1.0, 1.0, 1.0]
    light_specular =  [1.0, 1.0, 1.0, 1.0]
    light_position =  [-4.0, 3.0, 4.0, 0.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)

    # load geom data into display list
    global obj_mesh
    obj_mesh = obj_from_file(os.getcwd()+"/07_legacy_obj/bunny.obj")


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-8.0, 8.0, -8.0, 8.0, -10.0, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def keyboard(key, x, y):
    if key == chr(27):
        sys.exit(0)

# main
glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(250, 250)
glutInitWindowPosition(100, 100)
glutCreateWindow('OBJ File')
init()
glutKeyboardFunc(keyboard)
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutIdleFunc(spinDisplay)
glutMainLoop()
