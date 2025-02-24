#!/usr/bin/python

import sys
import numpy as np
from PIL import Image
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from obj_loader import *
from OpenGL.GL import shaders

spin = 0.0
spinSpeed = 0.01
nr_faces = 0
indices = None
vertices = None
ib = GL_NONE
vb = GL_NONE
program = GL_NONE

lambertTex = GL_NONE
heightTex = GL_NONE

# rendering options
wireframe = False
tessLevels = 1;


vertex_code = """
    #version 420 compatibility

    in vec3 position;
    in vec3 normal;
    in vec2 texCoords;

    out VertexData
    {
        vec3 normalVS;
        vec2 texCoords;
    } Out;

    void main()
    {
        Out.normalVS = normalize(gl_NormalMatrix * normal);
        Out.texCoords = texCoords;
        gl_Position = gl_ModelViewMatrix * vec4(position, 1.0f);
    } """
    
tess_cont_code = """
    #version 420 compatibility
 
    // tessellation levels
    uniform float uTessLevels = 1;
 
    layout(vertices = 3) out;
 
    in VertexData
    {
        vec3 normalVS;
        vec2 texCoords;
    } In[];
 
    out vec3 tcNormal[];
    out vec2 tcTexCoords[];
 
    void main()
    {
        // get data
        gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
        tcNormal[gl_InvocationID]           = In[gl_InvocationID].normalVS;
        tcTexCoords[gl_InvocationID]        = In[gl_InvocationID].texCoords;
        
        // set tess levels
        if(gl_InvocationID == 0)
        {
            gl_TessLevelInner[0] = uTessLevels;
            gl_TessLevelInner[1] = uTessLevels;
            gl_TessLevelOuter[0] = uTessLevels;
            gl_TessLevelOuter[1] = uTessLevels;
            gl_TessLevelOuter[2] = uTessLevels;
            gl_TessLevelOuter[3] = uTessLevels;
        }
    } """

tess_eval_code = """
    #version 420 compatibility
 
    layout(triangles) in;
 
    in vec3 tcNormal[];
    in vec2 tcTexCoords[];
 
    out VertexData
    {
        vec3 posVS;
        vec3 normalVS;
        vec2 texCoords;
    } Out;

    uniform sampler2D texHeight;
    uniform float heightScale = 1;
    
    void main()
    {
        vec3 p0 = gl_TessCoord.x * gl_in[0].gl_Position.xyz;
        vec3 p1 = gl_TessCoord.y * gl_in[1].gl_Position.xyz;
        vec3 p2 = gl_TessCoord.z * gl_in[2].gl_Position.xyz;
        vec3 pos = p0 + p1 + p2;

        vec3 n0 = gl_TessCoord.x * tcNormal[0];
        vec3 n1 = gl_TessCoord.y * tcNormal[1];
        vec3 n2 = gl_TessCoord.z * tcNormal[2];
        vec3 normal = normalize(n0 + n1 + n2);
        Out.normalVS = normal;

        vec2 tc0 = gl_TessCoord.x * tcTexCoords[0];
        vec2 tc1 = gl_TessCoord.y * tcTexCoords[1];
        vec2 tc2 = gl_TessCoord.z * tcTexCoords[2];  
        Out.texCoords = tc0 + tc1 + tc2;
        
        float height = texture(texHeight, Out.texCoords).r;
        pos += normal * (height * heightScale - 0.5*heightScale);
        gl_Position = gl_ProjectionMatrix * vec4(pos, 1);
        Out.posVS = pos;
    } """

fragment_code = """
    #version 420 compatibility
    
    in VertexData
    {
        vec3 posVS;
        vec3 normalVS;
        vec2 texCoords;
    } In;

    uniform sampler2D texColour;    
    uniform sampler2D texHeight;
    uniform float heightScale = 1;
    
    vec2 dHdxy_fwd(vec2 vUv)
    {
        vec2 dSTdx = dFdx( vUv );
        vec2 dSTdy = dFdy( vUv );

        float Hll = heightScale * texture( texHeight, vUv ).x;
        float dBx = heightScale * texture( texHeight, vUv + dSTdx ).x - Hll;
        float dBy = heightScale * texture( texHeight, vUv + dSTdy ).x - Hll;

        return vec2( dBx, dBy );
    }

    vec3 estimateNormal(vec3 surf_pos, vec3 surf_norm, vec2 dHdxy)
    {
        vec3 vSigmaX = dFdx( surf_pos );
        vec3 vSigmaY = dFdy( surf_pos );
        vec3 vN = surf_norm;		// normalized

        vec3 R1 = cross( vSigmaY, vN );
        vec3 R2 = cross( vN, vSigmaX );

        float fDet = dot( vSigmaX, R1 );

        vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
        return normalize( abs( fDet ) * surf_norm - vGrad );
    }

    void main()
    {
        // Estimate the normal
        vec2 der = dHdxy_fwd(In.texCoords);
        vec3 normal = estimateNormal(In.posVS, normalize(In.normalVS), der);
        
        vec3 lambert = texture(texColour, In.texCoords).rgb;
        float light = dot(normalize(-In.posVS), normal);
        
        gl_FragColor = vec4(light * lambert, 1);
    } """

def loadTexture(path):
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
    img_data = np.fromstring(img.tobytes(), np.uint8)
    width, height = img.size

    # glTexImage2D expects the first element of the image data to be the
    # bottom-left corner of the image.  Subsequent elements go left to right,
    # with subsequent lines going from bottom to top.

    # However, the image data was created with PIL Image tostring and numpy's
    # fromstring, which means we have to do a bit of reorganization. The first
    # element in the data output by tostring() will be the top-left corner of
    # the image, with following values going left-to-right and lines going
    # top-to-bottom.  So, we need to flip the vertical coordinate (y). 
    texture = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    if img.mode == 'RGB':
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
            GL_RGB, GL_UNSIGNED_BYTE, img_data)
    elif img.mode == 'RGBA':
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    return texture

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glPushMatrix()
    glRotatef(spin, 1.0, 0.0, 0.0)
    glTranslatef(0, 0.0, 4.0)
    glScalef(4.0, 4.0, 4.0)
    
    loc = glGetUniformLocation(program, "uTessLevels")
    glUniform1f(loc, tessLevels)
    
    loc = glGetUniformLocation(program, 'texHeight')
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, heightTex)
    glUniform1i(loc, 0)

    loc = glGetUniformLocation(program, 'texColour')
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, lambertTex)
    glUniform1i(loc, 1)

    glPatchParameteri(GL_PATCH_VERTICES, 3)
    glDrawElements(GL_PATCHES, 3*nr_faces, GL_UNSIGNED_INT, ctypes.c_void_p(0))
    
    glPopMatrix()
    glFinish()
    glutSwapBuffers()

def animate():
    global spin
    global spinSpeed

    if spinSpeed > 0:
        spin = spin + spinSpeed
        if (spin > 45.0):
            spinSpeed = -spinSpeed
    else:
        spin = spin + spinSpeed
        if (spin < -45.0):
            spinSpeed = -spinSpeed
    glutPostRedisplay()

def init():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    
    # load geom data into buffers
    mesh = obj_from_file('Plane.obj')

    global vertices
    vertices = np.zeros(len(mesh.vertices), [("position", np.float32, 3), ("normal", np.float32, 3), ("texCoords", np.float32, 2)])
    vertices['position']  = mesh.vertices
    vertices['normal']    = mesh.normals
    vertices['texCoords'] = mesh.texcoords
    
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

    offset = ctypes.c_void_p(vertices.dtype["position"].itemsize + vertices.dtype["normal"].itemsize)
    loc = glGetAttribLocation(program, "texCoords")
    glEnableVertexAttribArray(loc)
    glBindBuffer(GL_ARRAY_BUFFER, vb)
    glVertexAttribPointer(loc, 2, GL_FLOAT, False, stride, offset)

    # bind the index buffer
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ib)

    # Load the textures
    global lambertTex
    global heightTex
    lambertTex = loadTexture( 'PlaneMetal.jpg' )
    heightTex  = loadTexture( 'PlaneHeight.png' )



def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, float(w) / float(h), 0.1, 20)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 2, 4, 0, 0, 0, 0, 1, 0)

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
glutInitWindowSize(512, 512)
glutInitWindowPosition(100, 100)
glutCreateWindow('Subdivision using Tessellation Shaders')
init()
glutKeyboardFunc(keyboard)
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutIdleFunc(animate)

# Enter the main loop
glutMainLoop()
