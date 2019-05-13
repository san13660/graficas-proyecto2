# Christopher Sandoval 13660
# Proyecto 2

import pygame
import pyassimp
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import random
import numpy
import glm
from math import sin, cos

from shaders import vertex_shader, fragment_shader

def glize(node):
    model = node.transformation.astype(numpy.float32)

    for mesh in node.meshes:
        material = dict(mesh.material.properties.items())
        texture = material['file']

        texture_surface = pygame.image.load(texture)
        texture_data = pygame.image.tostring(texture_surface, "RGB", 1)
        width = texture_surface.get_width()
        height = texture_surface.get_height()

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        vertex_data = numpy.hstack((
            numpy.array(mesh.vertices, dtype=numpy.float32),
            numpy.array(mesh.normals, dtype=numpy.float32),
            numpy.array(mesh.texturecoords[0], dtype=numpy.float32)
        ))

        index_data = numpy.hstack((
            numpy.array(mesh.faces, dtype=numpy.int32)
        ))

        vertex_buffer_object = glGenVertexArrays(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, False, 9*4, None)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, False, 9*4, ctypes.c_void_p(3*4))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 3, GL_FLOAT, False, 9*4, ctypes.c_void_p(6*4))
        glEnableVertexAttribArray(2)


        element_buffer_object = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, element_buffer_object)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

        glUniformMatrix4fv(
            glGetUniformLocation(shader, "model"), 1, GL_FALSE, model
        )

        glUniformMatrix4fv(
            glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm.value_ptr(view)
        )

        glUniformMatrix4fv(
            glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection)
        )

        diffuse = mesh.material.properties['diffuse']

        glUniform4f(
            glGetUniformLocation(shader, "color"),
            *diffuse,
            1
        )

        glUniform4f(
            glGetUniformLocation(shader, "light"),
            0, 10, 10, 1
        )

        glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_INT, None)

    for child in node.children:
        glize(child)

def process_input():
    global camera_angle
    global camera_distance
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            elif event.key == pygame.K_f:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            if event.key == pygame.K_LEFT:
                camera_angle -= 0.1
            if event.key == pygame.K_RIGHT:
                camera_angle += 0.1
            if event.key == pygame.K_UP:
                camera_distance -= 2
            if event.key == pygame.K_DOWN:
                camera_distance += 2
            if event.key == pygame.K_a:
                camera.y += 2
            if event.key == pygame.K_z:
                camera.y -= 2

clock = pygame.time.Clock()

screen = pygame.display.set_mode((800, 600), pygame.OPENGL|pygame.DOUBLEBUF)

glClearColor(0.1,0.1,0.1,1.0)
glEnable(GL_DEPTH_TEST)
glEnable(GL_TEXTURE_2D)

shader = compileProgram(
    compileShader(vertex_shader, GL_VERTEX_SHADER),
    compileShader(fragment_shader, GL_FRAGMENT_SHADER)
)

glUseProgram(shader)

model = glm.mat4(1)
view = glm.mat4(1)
projection = glm.perspective(glm.radians(45), 800/600, 0.1, 1000.0)

glViewport(0, 0, 800, 600)

camera_angle = 0.0
camera_distance = 35
camera = glm.vec3(0, 0, camera_distance)

scene = pyassimp.load('hyrule_castle.obj')

while True:
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

    view = glm.lookAt(camera, glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))

    glize(scene.rootnode)

    pygame.display.flip()

    camera.x = sin(camera_angle) * camera_distance
    camera.z = cos(camera_angle) * camera_distance

    process_input()

    clock.tick(15)