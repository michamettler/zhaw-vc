from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.utils import  display_cube , update_vars, keyboard_handler, reshape_polygons

screen_width = 1000
screen_height = 800
background_color = (0.0, 0.0, 0.0, 1.0)


def init():
    R,G,B,A = background_color
    glClearColor(R,G,B,A) 
    glShadeModel(GL_FLAT)
    light_ambient =  [0.0, 0.0, 0.0, 1.0]
    light_diffuse =  [1.0, 1.0, 1.0, 1.0]
    light_specular =  [1.0, 1.0, 1.0, 1.0]
    light_position =  [0.0, 0.0, 4.0, 0.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glFrontFace(GL_CW)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)

def main():
    """
    Main function to set up the window and start the GLUT main loop.
    """
    # Initialize GLUT with command-line parameters.
    
    glutInit(sys.argv)
    # Set up display mode:
    # - GLUT_RGBA: use RGBA color mode.
    # - GLUT_DOUBLE: enable double buffering.
    # - GLUT_ALPHA: use an alpha channel.
    # - GLUT_DEPTH: enable depth buffering.
    glutInitDisplayMode(GLUT_RGBA|GLUT_DOUBLE|GLUT_ALPHA|GLUT_DEPTH)
    # Enable depth testing
    
    
    # Set up window size
    glutInitWindowSize(screen_width, screen_height)
    # Set up window position
    glutInitWindowPosition(0, 0)
    
    glutCreateWindow(b"PyOpenGL Window Setup")
    # initialize the context
    init()
        
    glutReshapeFunc(reshape_polygons)
    
    # Register the display callback function.
    glutDisplayFunc(display_cube)
    
    # Register the keyboard callback to handle key presses.
    glutKeyboardFunc(keyboard_handler)
    
    #register the idle callback to continuously update the window.
    glutIdleFunc(update_vars)
    
    # Enter the GLUT main loop.
    glutMainLoop()
    
if __name__ == "__main__":
    main()