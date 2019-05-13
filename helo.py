import pygame
import random
import numpy
import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

clock = pygame.time.Clock()

screen = pygame.display.set_mode((800, 600), pygame.OPENGL|pygame.DOUBLEBUF)

glClearColor(0.1,0.1,0.1,1.0)
glEnable(GL_DEPTH_TEST)

# shaders

vertex_shader = """
#version 330

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 colorsito;

uniform mat4 theMatrix;

out vec3 ourColor;

void main()
{
    gl_Position = theMatrix * vec4(position.x, position.y, position.z, 1);
    ourColor = colorsito;
}

"""

fragment_shader = """
#version 330

layout (location = 0) out vec4 fragColor;

in vec3 ourColor;

void main()
{
    fragColor = vec4(ourColor, 1);
}
"""

shader = compileProgram(
    compileShader(vertex_shader, GL_VERTEX_SHADER),
    compileShader(fragment_shader, GL_FRAGMENT_SHADER)
)

vertex_data = numpy.array([
     0.5,  0.5, 0.0, 1.0, 0.0, 0.0,
     0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
    -0.5, -0.5, 0.0, 0.0, 0.0, 1.0,
    -0.5,  0.5, 0.0, 1.0, 1.0, 0.0,
], dtype=numpy.float32)

index_data = numpy.array([
    0,1,3,
    1,2,3
], dtype = numpy.uint32)

vertex_array_object = glGenVertexArrays(1)
glBindVertexArray(vertex_array_object)

element_buffer_object = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, element_buffer_object)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

vertex_buffer_object = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

glVertexAttribPointer(
    0,                  # location para el shader
    3,                  # size
    GL_FLOAT,           # data type
    GL_FALSE,           # normalize?
    4 * 6,              # stride
    ctypes.c_void_p(0)  # pointer
)

glVertexAttribPointer(
    1,                  # location para el shader
    3,                  # size
    GL_FLOAT,           # data type
    GL_FALSE,           # normalize?
    4 * 6,              # stride
    ctypes.c_void_p(4 * 3)  # pointer
)

glEnableVertexAttribArray(0)
glEnableVertexAttribArray(1)

i = glm.mat4(1)

translate = glm.translate(i, glm.vec3(0, 0 , 0))
rotate = glm.rotate(i, 0, glm.vec3(0, 1, 0))
scale = glm.scale(i, glm.vec3(1, 1, 1))

model = translate * rotate * scale
view = glm.lookAt(glm.vec3(0, 0, 2), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
projection = glm.perspective(glm.radians(45), 800/600, 0.1, 1000.0)

theMatrix = projection * view * model

glViewport(0, 0, 800, 600)

glClearColor(1,0,0,1)

counter = 0

def process_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            elif event.key == pygame.K_f:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

while True:
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

    glUseProgram(shader)

    r = 0
    g = (numpy.sin(counter) / 4) + 0.5
    b = 0

    glUniformMatrix4fv(
        glGetUniformLocation(shader, 'theMatrix'), 
        1,
        GL_FALSE,
        glm.value_ptr(theMatrix)
    )

    colorLocation = glGetUniformLocation(shader, "ourColor")
    glUniform3f(colorLocation, r, g, b)

    #glDrawArrays(GL_TRIANGLES, 0, 3)
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

    pygame.display.flip()

    counter += 1

    process_input()

    clock.tick(15)