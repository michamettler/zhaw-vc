from OpenGL.GLUT import *
from OpenGL.GL import *

spin = 0.0

def display_rect():
    global spin
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glPushMatrix()
    glRotatef(spin, 0.0, 0.0, 1.0)
    glColor4f(0.0, 1.0, 1.0, 0.5)
    glRectf(-3.0, -3.0, 3.0, 3.0)
    glPopMatrix()
    glutSwapBuffers()
    
def display_polygons_with_depth():
    global spin
    glClear(GL_COLOR_BUFFER_BIT| GL_DEPTH_BUFFER_BIT )

    glPushMatrix()
    glColor3f(0.8, 0.1, 0.1)
    glBegin(GL_POLYGON)
    glVertex3f(-2.0, -2.0, 1.0)
    glVertex3f(2.0, -2.0, 1.0)
    glVertex3f(2.0, 2.0, 1.0)
    glVertex3f(-2.0, 2.0, 1.0)
    glEnd()
    glPopMatrix()

    glPushMatrix()
    glRotatef(spin, 0.0, 1.0, 0.0)
    glColor3f(0.4, 0.6, 0.8)
    glBegin(GL_TRIANGLE_STRIP)
    glVertex3f(0.0, 3.0, 5.0)
    glVertex3f(4.0, 3.0, 5.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(4.0, 0.0, 0.0)
    glVertex3f(0.0, -3.0, 0.0)
    glVertex3f(4.0, -3.0, 0.0)
    glEnd()
    glPopMatrix()

    glFlush ()
    glutSwapBuffers()
    

def display_polygons():
    global spin
    glClear(GL_COLOR_BUFFER_BIT )
    display_rect()
    display_polygon()
    glFlush ()
    glutSwapBuffers()

def display_rect():
    glPushMatrix()
    glColor3f(0.8, 0.1, 0.1)
    glBegin(GL_POLYGON)
    glVertex3f(-2.0, -2.0, 1.0)
    glVertex3f(2.0, -2.0, 1.0)
    glVertex3f(2.0, 2.0, 1.0)
    glVertex3f(-2.0, 2.0, 1.0)
    glEnd()
    glPopMatrix()
    
def display_polygon():
    glPushMatrix()
    glRotatef(spin, 0.0, 1.0, 0.0)
    glColor3f(0.4, 0.6, 0.8)
    glBegin(GL_TRIANGLE_STRIP)
    glVertex3f(0.0, 3.0, 5.0)
    glVertex3f(4.0, 3.0, 5.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(4.0, 0.0, 0.0)
    glVertex3f(0.0, -3.0, 0.0)
    glVertex3f(4.0, -3.0, 0.0)
    glEnd()
    glPopMatrix()
    
    
    
    
def display_cube():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPushMatrix()
    mat = [0.8, 0.1, 0.1, 0]
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, mat)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, mat)
    glutSolidSphere(1.0, 25, 25)
    glPopMatrix()

    glPushMatrix()
    glRotatef(spin, 0.0, 1.0, 0.0)
    glTranslatef(1.5, 0.0, 0.0)
    mat = [0.4, 0.6, 0.8, 0]
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, mat)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, mat)
    glutSolidCube(2.5)
    glPopMatrix()

    glFlush ()
    glutSwapBuffers()
    


def display_teapot():
    """Clears the screen, sets MODELVIEW, then draws the compiled teapot list."""
    global spin, teapotList

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glPushMatrix()
    glTranslatef(8.0, 8.0, 0.0)
    glRotatef(spin, 0.0, 1.0, 0.0)

    # Example material properties
    mat_ambient_diffuse = [0.8, 0.0, 0.0, 1.0]
    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient_diffuse)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_ambient_diffuse)

    mat_specular = [0.9, 0.9, 0.9, 1.0]
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, 90.0)

    # Draw the teapot from the display list
    glCallList(teapotList)

    glPopMatrix()
    glutSwapBuffers()
    
    
def display_empty():
    """
    Display callback function that clears the screen sand swaps the buffers
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    ## Any Drawing code would go here
    glutSwapBuffers()
    
def update_vars():
    global spin
    spin = spin + 1.0
    if spin > 360.0:
        spin = spin - 360.0
    glutPostRedisplay()
    
    
def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-5.0, 5.0, -5.0, 5.0, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def reshape_polygons(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-8.0, 8.0, -8.0, 8.0, -10.0, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def reshape_teapot(w, h):
    """Sets up the projection and modelview for the teapot scene."""
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-8.0, 8.0, -8.0, 8.0, -10.0, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
def reshape_teapot(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if (w <= h):
        glOrtho(0.0, 16.0, 0.0, 16.0 * h / w, -10.0, 10.0)
    else:
        glOrtho(0.0, 16.0 * w / h, 0.0, 16.0, -10.0, 10.0)
    glMatrixMode(GL_MODELVIEW)

def keyboard_handler(key,x,y):
    """
    Keyboard callback function.
    Exits the program when 'q' or the Escape key is pressed.
    """
    # Convert the byte string key to a standard string (Python 3 compatibility)
    key = key.decode("utf-8") if isinstance(key, bytes) else key

    if key in ['q', 'Q', '\x1b']: 
        print("Quit key pressed. Exiting program.")
        try:
            # Try to exit gracefully by leaving the GLUT main loop.
            glutLeaveMainLoop()
        except Exception:
            # If glutLeaveMainLoop() is not available, force exit immediately.
            os._exit(0)