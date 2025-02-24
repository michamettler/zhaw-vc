#! /usr/bin/env python
# MODERN OpenGL SAMPLE: COLORED RECTANGLE

import sys
import ctypes
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GL import shaders

vertex_code = """
    #version 420 compatibility

    uniform float scale;
    
    in vec4 color;
    in vec2 position;

    out vec4 vColor;

    void main()
    {
        gl_Position = vec4(scale*position, 0.0, 1.0);
        vColor = color;
    } """

tess_cont_code = """

    #version 420 compatibility

    layout(vertices = 4) out;

    in  vec4 vColor[];

    out vec4 tcColor[];

    uniform float TessLevelInner = 1;
    uniform float TessLevelOuter = 1;

    #define ID gl_InvocationID

    void main()
    {
        gl_out[ID].gl_Position = gl_in[ID].gl_Position;
        tcColor[ID]     = vColor[ID];

        if (ID == 0) {
            gl_TessLevelInner[0] = TessLevelInner;
            gl_TessLevelInner[1] = TessLevelInner;
            gl_TessLevelOuter[0] = TessLevelOuter;
            gl_TessLevelOuter[1] = TessLevelOuter;
            gl_TessLevelOuter[2] = TessLevelOuter;
            gl_TessLevelOuter[3] = TessLevelOuter;
        }
    }

"""

tess_eval_code = """

    #version 420 compatibility

    layout(quads) in;

    in vec4 tcColor[];

    out vec4 v_color;

    void main()
    {
        float u = gl_TessCoord.x;
        float v = gl_TessCoord.y;

        vec4 a = mix(gl_in[1].gl_Position, gl_in[0].gl_Position, u);
        vec4 b = mix(gl_in[2].gl_Position, gl_in[3].gl_Position, u);
        gl_Position = mix(a, b, v);
    
        a = mix(tcColor[1], tcColor[0], u);
        b = mix(tcColor[2], tcColor[3], u);
        v_color = mix(a, b, v);
    }

"""

fragment_code = """
    #version 420 compatibility

    in vec4 v_color;
    
    void main()
    {
        gl_FragColor = v_color;
    } """

# Uniforms
tessLevelInner = 1;
tessLevelOuter = 1;

# init data
data = np.zeros(4, [("position", np.float32, 2),
                    ("color",    np.float32, 4)])
data['color']    = [ (1,0,0,1), (0,1,0,1), (1,1,0,1), (0,0,1,1) ]
data['position'] = [ (-1,-1),   (-1,+1),   (+1,+1),   (+1,-1)   ]

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    loc = glGetUniformLocation(program, "TessLevelInner")
    glUniform1f(loc, tessLevelInner)
    loc = glGetUniformLocation(program, "TessLevelOuter")
    glUniform1f(loc, tessLevelOuter)

    glPatchParameteri(GL_PATCH_VERTICES, 4);
    glDrawArrays(GL_PATCHES, 0, 4)
    glutSwapBuffers()

def reshape(width,height):
    glViewport(0, 0, width, height)

def keyboard( bkey, x, y ):
    key = bkey.decode("utf-8")
    if key == '\033':
        sys.exit( )
        
    global tessLevelInner
    global tessLevelOuter
    if key == 'q': # increase outer tessellation
        tessLevelOuter += 1
        if tessLevelOuter > 64:
            tessLevelOuter = 64;
        glutPostRedisplay()
        print('Outer level: ' + str(tessLevelOuter))
        
    if key == 'a': # decrease outer tessellation
        tessLevelOuter -= 1
        if tessLevelOuter == 0:
            tessLevelOuter = 1;
        glutPostRedisplay()
        print('Outer level: ' + str(tessLevelOuter))
        
    if key == 'w': # increase inner tessellation
        tessLevelInner += 1
        if tessLevelInner > 64:
            tessLevelInner = 64;
        glutPostRedisplay()
        print('Inner level: ' + str(tessLevelInner))
        
    if key == 's': # decrease inner tessellation
        tessLevelInner -= 1
        if tessLevelInner == 0:
            tessLevelInner = 1;
        glutPostRedisplay()
        print('Inner level: ' + str(tessLevelInner))


# main
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
glutCreateWindow('Quad Tessellation')
glutReshapeWindow(512,512)
glutReshapeFunc(reshape)
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)

# setup GPU program
vertex = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
tess_cont = shaders.compileShader(tess_cont_code, GL_TESS_CONTROL_SHADER)
tess_eval = shaders.compileShader(tess_eval_code, GL_TESS_EVALUATION_SHADER)
fragment = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
program = shaders.compileProgram(vertex, tess_cont, tess_eval, fragment, validate=True)
glUseProgram(program)
buffer = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)

# bind attributes and uniforms
stride = data.strides[0]
offset = ctypes.c_void_p(0)
loc = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
glVertexAttribPointer(loc, 3, GL_FLOAT, False, stride, offset)
offset = ctypes.c_void_p(data.dtype["position"].itemsize)
loc = glGetAttribLocation(program, "color")
glEnableVertexAttribArray(loc)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
glVertexAttribPointer(loc, 4, GL_FLOAT, False, stride, offset)
loc = glGetUniformLocation(program, "scale")
glUniform1f(loc, 0.75)

# setup the states
glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

# run
glutMainLoop()
