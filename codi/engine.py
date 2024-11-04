import json
import pygame as pg
import moderngl as mgl
import glm
import sys

from camera import Camera
from light import Light
from axis import Axis
from object import Sun, Planet, StarBatch
import shaders as sh
from reader import Reader
from gui import ButtonManager
import os

class GraphicsEngine:
    """Classe que farà corre l'aplicació controlant instàcies de les altres classes 
    """

    def __init__(self, win_size=(900, 800)):
        """Inicialització de la classe GraphicsEngine

        Args:
            win_size (tuple, optional): Tamany de finestra de l'aplicació. Defaults to (900,800).
        """
        # init pygame modules
        pg.init()

        # window size
        self.WIN_SIZE = win_size

        # set opengl attr
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        # create opengl context
        pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.BLEND)

        # camera
        self.camera = Camera(self)

        # light
        self.light = Light()
        self.objects = []
        self.clock = pg.time.Clock()
        self.time = 0

        # gui
        self.button_manager = ButtonManager(self)

        with open(r"./codi/gui_layout.json", "r") as file:
            gui_layout = json.load(file)

        self.button_manager.batch_add_buttons(gui_layout)

        # axis
        # self.objects.append(Axis(self))

        # planetes

        # Opcions exemple per crear l'esfera: ["stripes", 1.0, 20, 20] o bé
        # ["octahedron", 2]
        planets_list = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
        planets_textures = ["textures/mercury.jpg", 
                            "textures/venus.jpg",
                            "textures/earth.jpg",
                            "textures/jupiter.jpg",
                            "textures/saturn.jpg",
                            "textures/uranus.jpg",
                            "textures/neptune.jpg"]
        planets_data = dict()

        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        for planet in planets_list:
            read_data = Reader.read_planets("data/planets.csv", planet) 
            planets_data[planet] = read_data

        #print(planets_data["Earth"].data["Mass (10^24kg)"], type(planets_data["Earth"].data["Mass (10^24kg)"]))

        #! IMPORTANT ANNOTATION: SUBJECTE A CANVIS
        # Scale radius: 1:100.000km 
        # Scale distance: 1:15*(10^6)km
        # Scale distance: 1:100km/h
        # Escalat planeta: x5 
        
        self.objects.append(Sun(
            self,
            [sh.vertex_shader_SUN, sh.fragment_shader_SUN],
            "textures/sun.jpg",
            ["stripes", 7, 20, 20], 
        ))
        for planet, texture in zip(planets_list, planets_textures):
            self.objects.append(Planet(
                self,
                [sh.vertex_shader_EARTH, sh.fragment_shader_EARTH],
                texture,
                ["stripes", planets_data[planet].data["Diameter (km)"]/200000, 15, 15],
                # la Terra. color, size i posició son els de la Terra by default
                # (de moment)
                glm.vec3(0, 0, 1),
                glm.vec3(5, 5, 5), 
                glm.vec3(planets_data[planet].data["Distance from Sun (10^6 km)"]/15, 0, planets_data[planet].data["Distance from Sun (10^6 km)"]/15),
                planets_data[planet].data["Orbital Velocity (km/s)"]/100,
                planets_data[planet].data["Orbital Inclination (degrees)"],
                planets_data[planet].data["Orbital Eccentricity"]
            ))

        # self.objects.append(Planet(
        #     self,
        #     [sh.vertex_shader_EARTH, sh.fragment_shader_EARTH],
        #     info_sphere,
        #     glm.vec3(1, 1, 1),
        #     glm.vec3(0.3, 0.3, 0.3),
        #     glm.vec3(0, 0, 8)
        # ))  # la Lluna

        # stars
        # self.st = Star(self, [sh.vertex_shader_STAR, sh.fragment_shader_STAR], "None", glm.vec3(3.5, 2.5, 0))
        star_reader = Reader.read_stars("data/hygdata_v41.csv")
        self.stars = star_reader.make_stars(StarBatch, [self, [sh.vertex_shader_STAR, sh.fragment_shader_STAR], "textures/earth.jpg", "None"]) #Won't put a texture

        # Informació relacionada amb el context de l'aplicació
        self.info = "Visualització del sol"

    def check_events(self):
        """Funcionalitat per controlar els events durant el temps de vida del programa.
        """
        self.button_manager.check_hover(pg.mouse.get_pos())

        for event in pg.event.get():
            if event.type == pg.QUIT or (
                    event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            ):
                self.end()

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.camera.left_button_held = True
                    self.camera.last_mouse_pos = pg.mouse.get_pos()

                button_event = self.button_manager.check_click(
                    pg.mouse.get_pos())
                if button_event == "day_picker":
                    print("Day picker pressed.")
                elif button_event == "zoom_in":
                    print("Zoom in pressed.")
                elif button_event == "zoom_out":
                    print("Zoom out pressed.")
                elif button_event == "constellations_visibility":
                    print("Constelations visibility pressed.")
                        # Mouse movement

            # Mouse button released
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    self.camera.left_button_held = False

            elif event.type == pg.MOUSEMOTION and self.camera.left_button_held:
                current_mouse_pos = pg.mouse.get_pos()
                if self.camera.last_mouse_pos is not None:
                    # Calculate difference in mouse movement
                    dx = current_mouse_pos[0] - self.camera.last_mouse_pos[0]
                    dy = current_mouse_pos[1] - self.camera.last_mouse_pos[1]

                    # Process the mouse movement to update camera rotation
                    self.camera.process_mouse_movement(dx, dy)

                # Update last mouse position
                self.camera.last_mouse_pos = current_mouse_pos

    def end(self):
        """
        Destruir tots els objectes i finalitzar la simulació.

        Returns
        -------
        None.

        """

        self.button_manager.destroy()

        for objecte in self.objects:
            objecte.destroy()

        self.stars.destroy()

        pg.quit()
        sys.exit()

    def get_time(self):
        """Funció per obtenir el temps (en ticks) - Ús: Fer rotar objectes
        """
        self.time = pg.time.get_ticks() * 0.001

    def render(self):
        """Renderització dels objectes 
        """
        # clear framebuffer
        self.ctx.clear(color=(0, 0, 0))

        # render gui
        self.button_manager.render()

        # render scene + axis
        for objecte in self.objects:
            objecte.render()

        # TODO: Are stars that can't be seen being processed/rendered?
        self.stars.render()

        # Swap buffers + display caption
        pg.display.set_caption(self.info)
        pg.display.flip()

    def run(self):
        """Funció per corre el programa frame a frame.
        """
        while True:
            self.get_time()
            self.check_events()
            self.camera.process_keyboard()
            self.render()
            self.clock.tick(60)
