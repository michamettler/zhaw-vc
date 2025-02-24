#!/usr/bin/python

import pyglet
import numpy as np
from pyglet.gl import *
# We still need PyOpenGL imports for the GL symbols and helpers
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL import shaders

# Our custom modules
from obj_loader import *
from trackball import *

# ---------------------
# GLOBALS & SHADERS
# ---------------------
spin = 0.0
trackball = Trackball(0,0,1,0.5)
wireframe = False
refine = False
smooth = False
renderNormals = False

nr_faces = 0
nr_vertices = 0
indices = None
vertices = None
ib = GL_NONE
vb = GL_NONE
program = GL_NONE
normalPrg = GL_NONE



vertex_code = """
	#version 330 compatibility
	
    in vec3 position;
    in vec3 normal;

    out VertexData
    {
        vec3 posVS;
        vec3 normalVS;
    };

    void main()
    {
        posVS = (gl_ModelViewMatrix * vec4(position, 1.0)).xyz;
        normalVS = normalize(gl_NormalMatrix * normal);
        gl_Position =  gl_ModelViewProjectionMatrix * vec4(position, 1.0f);
    } """
    
geometry_code = """
	#version 330 compatibility

    layout (triangles) in;
    layout (triangle_strip) out;
    layout (max_vertices = 12) out;

    in VertexData
    {
        vec3 posVS;
        vec3 normalVS;
    } In[];

    out VertexData
    {
        vec3 posVS;
        vec3 normalVS;
    } Out;

    uniform bool refine = false;
    uniform bool curved = false;

    float wij(int i, int j)
    {
        return dot(In[j].posVS - In[i].posVS, In[i].normalVS);
    }
 
    float vij(int i, int j)
    {
        vec3 Pj_minus_Pi = In[j].posVS - In[i].posVS;
        vec3 Ni_plus_Nj  = In[i].normalVS + In[j].normalVS;
        return 2.0 * dot(Pj_minus_Pi, Ni_plus_Nj) / dot(Pj_minus_Pi, Pj_minus_Pi);
    }

    #define b300    In[0].posVS
    #define b030    In[1].posVS
    #define b003    In[2].posVS
    #define n200    In[0].normalVS
    #define n020    In[1].normalVS
    #define n002    In[2].normalVS

    void main()
    {
        if (refine)
        {
            // Base
            vec3 P0 = In[0].posVS;
            vec3 P1 = In[1].posVS;
            vec3 P2 = In[2].posVS;
            vec3 N0 = In[0].normalVS;
            vec3 N1 = In[1].normalVS;
            vec3 N2 = In[2].normalVS;

            // Compute control points
            vec3 b210 = (2.0*P0 + P1 - wij(0,1) * N0) / 3.0;
            vec3 b120 = (2.0*P1 + P0 - wij(1,0) * N1) / 3.0;
            vec3 b021 = (2.0*P1 + P2 - wij(1,2) * N1) / 3.0;
            vec3 b012 = (2.0*P2 + P1 - wij(2,1) * N2) / 3.0;
            vec3 b102 = (2.0*P2 + P0 - wij(2,0) * N2) / 3.0;
            vec3 b201 = (2.0*P0 + P2 - wij(0,2) * N0) / 3.0;
            vec3 E = ( b210 + b120 + b021 + b012 + b102 + b201 ) / 6.0;
            vec3 V = (P0 + P1 + P2) / 3.0;
            vec3 b111 = E + (E - V) * 0.5;
            vec3 n110 = N0 + N1 - vij(0,1) * (P1 - P0);
            vec3 n011 = N1 + N2 - vij(1,2) * (P2 - P1);
            vec3 n101 = N2 + N0 - vij(2,0) * (P0 - P2);

            vec3 coords[6];
            coords[0] = vec3(0, 0, 1);
            coords[1] = vec3(1, 0, 0);
            coords[2] = vec3(0, 1, 0);
            coords[3] = vec3(0.5, 0, 0.5);
            coords[4] = vec3(0.5, 0.5, 0);
            coords[5] = vec3(0, 0.5, 0.5);

            vec3 v[6], n[6];
            for (int i = 0; i < 6; i++)
            {
                vec3 uvw = coords[i];

                n[i]
                = n200*uvw[2]
                + n020*uvw[0]
                + n002*uvw[1];

                v[i]
                = b300*uvw[2]
                + b030*uvw[0]
                + b003*uvw[1];
            }
            
            int idx[12];
            idx[0] = 0; idx[ 1] = 3; idx[ 2] = 5;
            idx[3] = 3; idx[ 4] = 1; idx[ 5] = 4;
            idx[6] = 4; idx[ 7] = 2; idx[ 8] = 5;
            idx[9] = 3; idx[10] = 4; idx[11] = 5;
            
            for (int t = 0; t < 4; t++)
            {
                for (int i = 0; i < 3; i++)
                {
                    vec3 p = v[idx[3*t+i]];
                    Out.posVS = p;
                    Out.normalVS = n[idx[3*t+i]];
                    gl_Position =  gl_ProjectionMatrix * vec4(p, 1.0f);
                    EmitVertex();
                }
                EndPrimitive();
            }
        }
        else
        {
            for (int i = 0; i < 3; i++)
            {
                Out.posVS = In[i].posVS;
                Out.normalVS = In[i].normalVS;
                gl_Position = gl_in[i].gl_Position;
                EmitVertex();
            }
            EndPrimitive();
        }
    } """

fragment_code = """
	#version 330 compatibility
	
    in VertexData
    {
        vec3 posVS;
        vec3 normalVS;
    };

    void main()
    {
        float lambert = dot(normalize(-posVS), normalize(normalVS));
        
        gl_FragColor = vec4(lambert, 0, lambert, 1);
    } """
    
nrm_vertex_code = """
	#version 330 compatibility
	
    in vec3 position;
    in vec3 normal;

    out VertexData
    {
        vec3 posVS;
        vec3 normalVS;
    };

    void main()
    {
        posVS = (gl_ModelViewMatrix * vec4(position, 1.0)).xyz;
        normalVS = normalize(gl_NormalMatrix * normal);
        gl_Position =  gl_ModelViewProjectionMatrix * vec4(position, 1.0f);
    } """
   
nrm_geometry_code = """
	#version 330 compatibility

    layout (points) in;
    layout (line_strip) out;
    layout (max_vertices = 2) out;

    in VertexData
    {
        vec3 posVS;
        vec3 normalVS;
    } In[];
    
    void main()
    {
        vec3 beg = In[0].posVS;
        vec3 end = beg + 0.05f * In[0].normalVS;
        gl_Position = gl_ProjectionMatrix * vec4(beg, 1);
        EmitVertex();
        gl_Position = gl_ProjectionMatrix * vec4(end, 1);
        EmitVertex();
 
        EndPrimitive();
    } """

nrm_fragment_code = """
	#version 330 compatibility
	
    void main()
    {        
        gl_FragColor = vec4(0.2, 0.8, 0.2, 1);
    } """
    
mouse = [0,0,-1,-1]

# ---------------------
# WINDOW & CONFIG
# ---------------------
config = Config(
    double_buffer=True,
    major_version=3,
    minor_version=3,
    depth_size=24,
    # stencil_size=8
)

window = pyglet.window.Window(
    width=800, height=600,
    caption="Tessellation using Geometry Shaders",
    resizable=True,
    config=config
)

# ---------------------
# INIT GL
# ---------------------
def init_gl():
    global nr_vertices, nr_faces, vertices, indices
    global vb, ib, program, normalPrg

    glClearColor(0, 0, 0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    # Load mesh
    mesh = obj_from_file('bunny.obj')
    nr_vertices = len(mesh.vertices)
    vertices = np.zeros(len(mesh.vertices),
        [("position", np.float32, 3), ("normal", np.float32, 3)]
    )
    vertices['position'] = mesh.vertices
    vertices['normal']   = mesh.normals

    faces = []
    for face in mesh.faces:
        v, n, t, m = face
        faces.append([v[0]-1, v[1]-1, v[2]-1])
    nr_faces = len(faces)

    indices = np.zeros(nr_faces, [("indices", np.int32, 3)])
    indices['indices'] = faces

    # Compile main program
    v_sh = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
    g_sh = shaders.compileShader(geometry_code, GL_GEOMETRY_SHADER)
    f_sh = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)
    program = shaders.compileProgram(v_sh, g_sh, f_sh)

    # Compile normal program
    nv_sh = shaders.compileShader(nrm_vertex_code, GL_VERTEX_SHADER)
    ng_sh = shaders.compileShader(nrm_geometry_code, GL_GEOMETRY_SHADER)
    nf_sh = shaders.compileShader(nrm_fragment_code, GL_FRAGMENT_SHADER)
    normalPrg = shaders.compileProgram(nv_sh, ng_sh, nf_sh)

    # Create buffers
    vb = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vb)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)

    ib = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ib)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_DYNAMIC_DRAW)

    # Setup attributes in main program
    glUseProgram(program)
    stride = vertices.strides[0]
    offset = ctypes.c_void_p(0)

    loc = glGetAttribLocation(program, "position")
    glEnableVertexAttribArray(loc)
    glVertexAttribPointer(loc, 3, GL_FLOAT, False, stride, offset)

    offset = ctypes.c_void_p(vertices.dtype["position"].itemsize)
    loc = glGetAttribLocation(program, "normal")
    glEnableVertexAttribArray(loc)
    glVertexAttribPointer(loc, 3, GL_FLOAT, False, stride, offset)

    glUseProgram(0)

# ---------------------
# PYGLET EVENT HANDLERS
# ---------------------
@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    trackball.push()
    glRotatef(spin, 0.0, 1.0, 0.0)
    glTranslatef(0, -0.1, 0.0)

    # Draw main object
    glUseProgram(program)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ib)
    glDrawElements(GL_TRIANGLES, 3*nr_faces, GL_UNSIGNED_INT, ctypes.c_void_p(0))

    if renderNormals:
        glUseProgram(normalPrg)
        glDrawArrays(GL_POINTS, 0, nr_vertices)

    trackball.pop()
    glUseProgram(0)

@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90.0, float(width)/float(height), 0.1, 20.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    return pyglet.event.EVENT_HANDLED

@window.event
def on_key_press(symbol, modifiers):
    global wireframe, refine, smooth, renderNormals

    if symbol == pyglet.window.key.ESCAPE:
        pyglet.app.exit()

    elif symbol == pyglet.window.key.W:
        wireframe = not wireframe
        mode = GL_LINE if wireframe else GL_FILL
        glPolygonMode(GL_FRONT_AND_BACK, mode)
        print("Wireframe:", wireframe)

    elif symbol == pyglet.window.key.R:
        refine = not refine
        loc = glGetUniformLocation(program, "refine")
        glUseProgram(program)
        glUniform1i(loc, 1 if refine else 0)
        print("Refine:", refine)

    elif symbol == pyglet.window.key.S:
        smooth = not smooth
        loc = glGetUniformLocation(program, "curved")
        glUseProgram(program)
        glUniform1i(loc, 1 if smooth else 0)
        print("Smooth:", smooth)

    elif symbol == pyglet.window.key.N:
        renderNormals = not renderNormals
        print("Normals:", renderNormals)

    window.invalidate()

@window.event
def on_mouse_press(x, y, button, modifiers):
    mouse[0], mouse[1] = x, y
    mouse[2], mouse[3] = button, 1

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    # If left mouse is dragging
    if buttons & pyglet.window.mouse.LEFT:
        viewport = glGetIntegerv(GL_VIEWPORT)
        old_x, old_y = mouse[0], mouse[1]
        mouse[0], mouse[1] = x, y

        # Convert to top-down or just pass raw if your trackball does it
        # Example inverting Y:
        inv_old_y = viewport[3] - old_y
        inv_y = viewport[3] - y

        trackball.drag_to(
            old_x, inv_old_y,
            dx, -dy  # might invert dy if you want the same "direction" as GLUT
        )
        window.invalidate()

# ---------------------
# ANIMATE THE SPIN
# ---------------------
def update(dt):
    global spin
    spin += 0.1
    if spin > 360.0:
        spin -= 360.0
    # Force redraw
    window.invalidate()
