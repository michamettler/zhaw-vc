# main.py

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import os

# Ensure Python can find "utils"
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.utils import  reshape_teapot

screen_width = 1000
screen_height = 800
background_color = (0.0, 0.0, 0.0, 1.0)

def init():
    """Sets up background color, basic lighting, and depth testing."""
    R, G, B, A = background_color
    glClearColor(R, G, B, A)
    glShadeModel(GL_FLAT)

    # Basic light parameters
    light_ambient   = [0.0, 0.0, 0.0, 1.0]
    light_diffuse   = [1.0, 1.0, 1.0, 1.0]
    light_specular  = [1.0, 1.0, 1.0, 1.0]
    light_position  = [0.0, 0.0, 4.0, 0.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT,  light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    # Front faces are clockwise; enable lighting & depth
    glFrontFace(GL_CW)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)

def initTeapotDisplayList():
    """Builds a single display list containing a solid teapot."""
    _teapotList = glGenLists(1)
    glNewList(_teapotList, GL_COMPILE)
    glutSolidTeapot(3.0)
    glEndList()
    return _teapotList

def main():
    """Main function to create a GLUT window, init OpenGL, and start the loop."""
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(screen_width, screen_height)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"PyOpenGL Teapot Demo")

    # 1) Initialize OpenGL state
    init()

    # 2) Build the teapot display list now that we have a valid context
    from utils import utils  # Import inside main so the context is ready
    utils.teapotList = initTeapotDisplayList()

    # 3) Set reshape callback to define projection
    glutReshapeFunc(reshape_teapot)

    # 4) Set display callback
    glutDisplayFunc(utils.display_teapot)

    # 5) Set keyboard & idle callbacks
    glutKeyboardFunc(utils.keyboard_handler)
    glutIdleFunc(utils.update_vars)

    # 6) Enter the GLUT event-processing loop
    glutMainLoop()

if __name__ == "__main__":
    main()
