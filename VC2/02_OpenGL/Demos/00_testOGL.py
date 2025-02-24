#!/usr/bin/python
# TEST PyOpenGL INSTALLATION

import sys

try:
  from OpenGL.GLUT import *
  from OpenGL.GL import *
except:
  print("ERROR: PyOpenGL not installed properly.")
  sys.exit()

def display():
   glClear(GL_COLOR_BUFFER_BIT)
   glColor3f(0.0, 1.0, 0.0)
   glBegin(GL_POLYGON)
   glVertex3f(0.25, 0.25, 0.0)
   glVertex3f(0.75, 0.25, 0.0)
   glVertex3f(0.75, 0.75, 0.0)
   glVertex3f(0.25, 0.75, 0.0)
   glEnd()
   glFlush ()

def init():
   glClearColor(0.0, 0.0, 0.0, 0.0)
   glMatrixMode(GL_PROJECTION)
   glLoadIdentity()
   glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)

#  main
glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(250, 250)
glutInitWindowPosition(100, 100)
glutCreateWindow("test")
init()
glutDisplayFunc(display)
glutMainLoop()
