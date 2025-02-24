#!/usr/bin/python

import sys
import numpy as np
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from obj_loader import *
from OpenGL.GL import shaders

spin = 0.0
nr_faces = 0
indices = None
vertices = None
ib = GL_NONE
vb = GL_NONE
program = GL_NONE

# rendering options
wireframe = False
refine = False
smooth = False
tessLevels = 1


vertex_code = """
    #version 420 compatibility

    in vec3 position;
    in vec3 normal;

    out VertexData
    {
        vec3 normalVS;
    } Out;

    void main()
    {
        Out.normalVS = normalize(gl_NormalMatrix * normal);
        gl_Position = gl_ModelViewMatrix * vec4(position, 1.0f);
    } """
    
tess_cont_code = """
    #version 420 compatibility
 
    // PN patch data
    struct PnPatch
    {
        float b210;
        float b120;
        float b021;
        float b012;
        float b102;
        float b201;
        float b111;
        float n110;
        float n011;
        float n101;
    };
 
    // tessellation levels
    uniform float uTessLevels = 1;
 
    layout(vertices = 3) out;
 
    in VertexData
    {
        vec3 normalVS;
    } In[];
 
    out vec3 pnNormal[3];
    out PnPatch pnPatch[3];
 
    float wij(int i, int j)
    {
        return dot(gl_in[j].gl_Position.xyz - gl_in[i].gl_Position.xyz, In[i].normalVS);
    }
 
    float vij(int i, int j)
    {
        vec3 Pj_minus_Pi = gl_in[j].gl_Position.xyz
                         - gl_in[i].gl_Position.xyz;
        vec3 Ni_plus_Nj  = In[i].normalVS+In[j].normalVS;
        return 2.0*dot(Pj_minus_Pi, Ni_plus_Nj)/dot(Pj_minus_Pi, Pj_minus_Pi);
    }
 
    void main()
    {
     // get data
     gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
     pnNormal[gl_InvocationID]           = In[gl_InvocationID].normalVS;
 
     // set base 
     float P0 = gl_in[0].gl_Position[gl_InvocationID];
     float P1 = gl_in[1].gl_Position[gl_InvocationID];
     float P2 = gl_in[2].gl_Position[gl_InvocationID];
     float N0 = In[0].normalVS[gl_InvocationID];
     float N1 = In[1].normalVS[gl_InvocationID];
     float N2 = In[2].normalVS[gl_InvocationID];
 
     // compute control points
     pnPatch[gl_InvocationID].b210 = (2.0*P0 + P1 - wij(0,1)*N0)/3.0;
     pnPatch[gl_InvocationID].b120 = (2.0*P1 + P0 - wij(1,0)*N1)/3.0;
     pnPatch[gl_InvocationID].b021 = (2.0*P1 + P2 - wij(1,2)*N1)/3.0;
     pnPatch[gl_InvocationID].b012 = (2.0*P2 + P1 - wij(2,1)*N2)/3.0;
     pnPatch[gl_InvocationID].b102 = (2.0*P2 + P0 - wij(2,0)*N2)/3.0;
     pnPatch[gl_InvocationID].b201 = (2.0*P0 + P2 - wij(0,2)*N0)/3.0;
     float E = ( pnPatch[gl_InvocationID].b210
               + pnPatch[gl_InvocationID].b120
               + pnPatch[gl_InvocationID].b021
               + pnPatch[gl_InvocationID].b012
               + pnPatch[gl_InvocationID].b102
               + pnPatch[gl_InvocationID].b201 ) / 6.0;
     float V = (P0 + P1 + P2)/3.0;
     pnPatch[gl_InvocationID].b111 = E + (E - V)*0.5;
     pnPatch[gl_InvocationID].n110 = N0+N1-vij(0,1)*(P1-P0);
     pnPatch[gl_InvocationID].n011 = N1+N2-vij(1,2)*(P2-P1);
     pnPatch[gl_InvocationID].n101 = N2+N0-vij(2,0)*(P0-P2);
 
     // set tess levels
     gl_TessLevelOuter[gl_InvocationID] = uTessLevels;
     gl_TessLevelInner[0] = uTessLevels;
    } """

tess_eval_code = """
    #version 420 compatibility
 
    // PN patch data
    struct PnPatch
    {
        float b210;
        float b120;
        float b021;
        float b012;
        float b102;
        float b201;
        float b111;
        float n110;
        float n011;
        float n101;
    };
 
    uniform float uTessAlpha = 1;          // controls the deformation
 
    layout(triangles) in;
 
    in vec3 pnNormal[];
    in PnPatch pnPatch[];
 
    out VertexData
    {
        vec3 posVS;
        vec3 normalVS;
    } Out;
 
    #define b300    gl_in[0].gl_Position.xyz
    #define b030    gl_in[1].gl_Position.xyz
    #define b003    gl_in[2].gl_Position.xyz
    #define n200    pnNormal[0]
    #define n020    pnNormal[1]
    #define n002    pnNormal[2]
    #define uvw     gl_TessCoord
 
    void main()
    {
        vec3 uvwSquared = uvw*uvw;
        vec3 uvwCubed   = uvwSquared*uvw;
 
        // extract control points
        vec3 b210 = vec3(pnPatch[0].b210, pnPatch[1].b210, pnPatch[2].b210);
        vec3 b120 = vec3(pnPatch[0].b120, pnPatch[1].b120, pnPatch[2].b120);
        vec3 b021 = vec3(pnPatch[0].b021, pnPatch[1].b021, pnPatch[2].b021);
        vec3 b012 = vec3(pnPatch[0].b012, pnPatch[1].b012, pnPatch[2].b012);
        vec3 b102 = vec3(pnPatch[0].b102, pnPatch[1].b102, pnPatch[2].b102);
        vec3 b201 = vec3(pnPatch[0].b201, pnPatch[1].b201, pnPatch[2].b201);
        vec3 b111 = vec3(pnPatch[0].b111, pnPatch[1].b111, pnPatch[2].b111);
 
     // extract control normals
     vec3 n110 = normalize(vec3(pnPatch[0].n110,
                                pnPatch[1].n110,
                                pnPatch[2].n110));
     vec3 n011 = normalize(vec3(pnPatch[0].n011,
                                pnPatch[1].n011,
                                pnPatch[2].n011));
     vec3 n101 = normalize(vec3(pnPatch[0].n101,
                                pnPatch[1].n101,
                                pnPatch[2].n101));
 
     // normal
     vec3 barNormal = gl_TessCoord[2]*pnNormal[0]
                    + gl_TessCoord[0]*pnNormal[1]
                    + gl_TessCoord[1]*pnNormal[2];
     vec3 pnNormal  = n200*uvwSquared[2]
                    + n020*uvwSquared[0]
                    + n002*uvwSquared[1]
                    + n110*uvw[2]*uvw[0]
                    + n011*uvw[0]*uvw[1]
                    + n101*uvw[2]*uvw[1];
     Out.normalVS = uTessAlpha*pnNormal + (1.0-uTessAlpha)*barNormal;
 
     // compute interpolated pos
     vec3 barPos = gl_TessCoord[2]*b300
                 + gl_TessCoord[0]*b030
                 + gl_TessCoord[1]*b003;
 
     // save some computations
     uvwSquared *= 3.0;
 
     // compute PN position
     vec3 pnPos  = b300*uvwCubed[2]
                 + b030*uvwCubed[0]
                 + b003*uvwCubed[1]
                 + b210*uvwSquared[2]*uvw[0]
                 + b120*uvwSquared[0]*uvw[2]
                 + b201*uvwSquared[2]*uvw[1]
                 + b021*uvwSquared[0]*uvw[1]
                 + b102*uvwSquared[1]*uvw[2]
                 + b012*uvwSquared[1]*uvw[0]
                 + b111*6.0*uvw[0]*uvw[1]*uvw[2];
 
     // final position and normal
     vec3 finalPos = (1.0-uTessAlpha)*barPos + uTessAlpha*pnPos;
     Out.posVS = finalPos;
     gl_Position   = gl_ProjectionMatrix * vec4(finalPos,1.0);
    } """

fragment_code = """
    #version 420 compatibility
    
    in VertexData
    {
        vec3 posVS;
        vec3 normalVS;
    } In;

    void main()
    {
        float lambert = dot(normalize(-In.posVS), normalize(In.normalVS));
        
        gl_FragColor = vec4(lambert, 0, lambert, 1);
    } """

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glPushMatrix()
    glRotatef(spin, 0.0, 1.0, 0.0)
    glTranslatef(0, -5.0, 0.0)
    glScalef(40.0, 40.0, 40.0)
    
    loc = glGetUniformLocation(program, "uTessLevels")
    glUniform1f(loc, tessLevels)

    glPatchParameteri(GL_PATCH_VERTICES, 3)
    glDrawElements(GL_PATCHES, 3*nr_faces, GL_UNSIGNED_INT, ctypes.c_void_p(0))
    
    glPopMatrix()
    glFinish()
    glutSwapBuffers()

def spinDisplay():
    global spin
    spin = spin + 0.1
    if (spin > 360.0):
        spin = spin - 360.0
    glutPostRedisplay()

def init():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    
    # load geom data into buffers
    mesh = obj_from_file('bunny.obj')

    global vertices
    vertices = np.zeros(len(mesh.vertices), [("position", np.float32, 3), ("normal", np.float32, 3)])
    vertices['position'] = mesh.vertices
    vertices['normal']   = mesh.normals
    
    faces = []
    for face in mesh.faces:
        v, n, t, m = face
        faces.append([v[0] - 1, v[1] - 1, v[2] - 1])
    
    global nr_faces
    nr_faces = len(faces)

    global indices
    indices = np.zeros(nr_faces, [("indices", np.int32, 3)])
    indices['indices'] = faces

    # setup GPU program
    global program
    vertex = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
    tess_cont = shaders.compileShader(tess_cont_code, GL_TESS_CONTROL_SHADER)
    tess_eval = shaders.compileShader(tess_eval_code, GL_TESS_EVALUATION_SHADER)
    fragment = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
    program = shaders.compileProgram(vertex, tess_cont, tess_eval, fragment, validate=True)
    glUseProgram(program)

    global vb
    vb = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vb)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
    
    global ib
    ib = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ib)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_DYNAMIC_DRAW)
    
    # bind attributes and uniforms
    stride = vertices.strides[0]
    offset = ctypes.c_void_p(0)
    loc = glGetAttribLocation(program, "position")
    glEnableVertexAttribArray(loc)
    glBindBuffer(GL_ARRAY_BUFFER, vb)
    glVertexAttribPointer(loc, 3, GL_FLOAT, False, stride, offset)
    offset = ctypes.c_void_p(vertices.dtype["position"].itemsize)
    loc = glGetAttribLocation(program, "normal")
    glEnableVertexAttribArray(loc)
    glBindBuffer(GL_ARRAY_BUFFER, vb)
    glVertexAttribPointer(loc, 3, GL_FLOAT, False, stride, offset)

    # bind the index buffer
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ib)


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, float(w) / float(h), 0.1, 20)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(3, 3, 3, 0, 0, 0, 0, 1, 0)

def keyboard(bkey, x, y):
    key = bkey.decode("utf-8")
    if key == chr(27):
        sys.exit(0)

    if key == 'w':
        global wireframe
        wireframe = not wireframe
        if wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        print("Wireframe: " + str(wireframe))
            
    if key == 'r':
        global refine
        refine = not refine
        
        loc = glGetUniformLocation(program, "uTessLevels")
        if refine:
            glUniform1f(loc, 8)
        else:
            glUniform1f(loc, 1)
            
        print("Refine: " + str(refine))

    if key == 's':
        global smooth
        smooth = not smooth
        
        loc = glGetUniformLocation(program, "uTessAlpha")
        if smooth:
            glUniform1f(loc, 1)
        else:
            glUniform1f(loc, 0)
            
        print("Smooth: " + str(smooth))

        
    global tessLevels
    if key == '2': # increase tessellation
        tessLevels += 1
        if tessLevels > 64:
            tessLevels = 64;
        glutPostRedisplay()
        print('Tessellation level: ' + str(tessLevels))
        
    if key == '1': # decrease tessellation
        tessLevels -= 1
        if tessLevels == 0:
            tessLevels = 1;
        glutPostRedisplay()
        print('Tessellation level: ' + str(tessLevels))

# main
glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(250, 250)
glutInitWindowPosition(100, 100)
glutCreateWindow('Subdivision using Tessellation Shaders')
init()
glutKeyboardFunc(keyboard)
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutIdleFunc(spinDisplay)

# Enter the main loop
glutMainLoop()
