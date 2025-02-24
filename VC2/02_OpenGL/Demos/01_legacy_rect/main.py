from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.utils import  display_rect, update_vars, keyboard_handler, reshape

screen_width = 1000
screen_height = 800
background_color = (0.0, 0.0, 0.0, 1.0)


    
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
    glutInitDisplayMode(GLUT_RGBA|GLUT_DOUBLE|GLUT_ALPHA |GLUT_DEPTH)
    
    # Set up window size
    glutInitWindowSize(screen_width, screen_height)
    # Set up window position
    glutInitWindowPosition(0, 0)
    
    glutCreateWindow(b"PyOpenGL Window Setup")
    # initialize the context
    R,G,B,A = background_color
    glClearColor(R,G,B,A) 
    
    glutReshapeFunc(reshape)
    
    # Register the display callback function.
    glutDisplayFunc(display_rect)
    
    # Register the keyboard callback to handle key presses.
    glutKeyboardFunc(keyboard_handler)
    
    #register the idle callback to continuously update the window.
    glutIdleFunc(update_vars)
    
    # Enter the GLUT main loop.
    glutMainLoop()
    
if __name__ == "__main__":
    main()