import pygame as pg
import moderngl as mgl
import glm
import sys

from camera import Camera
from light import Light
from axis import Axis
from object import Sun, Planet
import shaders as sh

class GraphicsEngine:
    def __init__(self, win_size=(900,800)):
        # init pygame modules
        pg.init()
        # window size
        self.WIN_SIZE = win_size
        # set opengl attr
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION,3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        # create opengl context
        pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST)
        # camera
        self.camera = Camera(self)
        # light
        self.light = Light()
        self.objects = []
        # axis 
        self.objects.append(Axis(self))
        # planetes
        # Opcions exemple per crear l'esfera: ["stripes", 1.0, 20, 20] o bé ["octahedron", 2]
        info_sphere = ["octahedron", 3]
        self.objects.append(Sun(self, [sh.vertex_shader_SUN, sh.fragment_shader_SUN], ["stripes", 1.25, 20, 20]))
        self.objects.append(Planet(self, [sh.vertex_shader_EARTH, sh.fragment_shader_EARTH], info_sphere, glm.vec3(0,0,1), glm.vec3(0.5,0.5,0.5), glm.vec3(4,0,4))) # la Terra. color, size i posició son els de la Terra by default (de moment)
        self.objects.append(Planet(self, [sh.vertex_shader_EARTH, sh.fragment_shader_EARTH], info_sphere, glm.vec3(1,1,1), glm.vec3(0.3,0.3,0.3), glm.vec3(0,0,6))) # la Lluna
        # Informació relacionada amb el context de l'aplicació
        self.info = "Visualització del sol"
        
    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                for objecte in self.objects:
                    objecte.destroy()
                pg.quit()
                sys.exit()

    def render(self):
        # clear framebuffer
        self.ctx.clear(color=(0,0,0))

        # render scene + axis
        for objecte in self.objects:
            objecte.render()

        # Swap buffers + display caption
        pg.display.set_caption(self.info)
        pg.display.flip()

    def run(self):
        while True:
            self.check_events()
            self.render()
            
