import json
import pygame as pg
import moderngl as mgl
import glm
import sys

from camera import Camera
from light import Light
#from axis import Axis
from object import Sun, Planet, Satellite, Orbit, StarBatch
import shaders as sh
from reader import Reader
from gui import ButtonManager
import os

# Conversión a unidades astronómicas (UA)
ua_conversion = 149_600_000  # 1 UA en kilómetros


class GraphicsEngine:

    """Classe que farà corre l'aplicació controlant instàcies de les altres classes 
    """

    __slots__ = (
        "WIN_SIZE", 
        "ctx",
        "camera",
        "light",
        "objects",
        "orbits",
        "clock",
        "time",
        "button_manager",
        "stars",
        "info",
        "ellipse",
        "planets_list",
        "planets_textures",
        "satellites_textures",
        "planets_data"
    )

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
        self.orbits = []
        self.clock = pg.time.Clock()
        self.time = 0

        # gui
        self.button_manager = ButtonManager(self)

        with open(r"./codi/gui_layout.json", "r") as file:
            gui_layout = json.load(file)

        self.button_manager.batch_add_buttons(gui_layout)

        #self.create_objects()
        self.create_objects_modified()
        # axis
        # self.objects.append(Axis(self))

        # Informació relacionada amb el context de l'aplicació
        self.info = "Visualització del sol"
        self.ellipse = True

    def obtain_data_planets(self):
        planets_data = dict()
        
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        for planet in self.planets_list:
            read_data = Reader.read_planets("data/planets.csv", planet) 
            planets_data[planet] = read_data

        return planets_data
    
    @staticmethod
    def normalize(value, min_value, max_value, new_min, new_max):
        # Normalización min-max
        return ((value - min_value) / (max_value - min_value)) * (new_max - new_min) + new_min

    def radius_distance_objects(self):        
        # Radios y distancias sin escalar (en UA) para calcular valores min y max
        raw_radii = {"Sun": 696000 / ua_conversion}
        raw_distances = {}

        for planet in self.planets_list:
            # Almacenar radios y distancias en UA sin normalizar
            raw_radii[planet] = (self.planets_data[planet].data["Diameter (km)"] / 2) / ua_conversion
            raw_distances[planet] = (self.planets_data[planet].data["Distance from Sun (10^6 km)"] * 1e6) / ua_conversion

        # Satélites
        satellites_reader = Reader.read_satellites("data/satellites_modified.csv") 
        for index, row in satellites_reader.data.iterrows():
            name = row['name']
            raw_radii[name] = row['radius'] / ua_conversion

        # Encontrar los valores mínimo y máximo para normalización
        min_radius, max_radius = min(raw_radii.values()), max(raw_radii.values())
        min_distance, max_distance = min(raw_distances.values()), max(raw_distances.values())

        # Normalizar a los rangos deseados
        normalized_radii = {name: self.normalize(radius, min_radius, max_radius, 0.0001, 20) for name, radius in raw_radii.items()}
        normalized_distances = {name: self.normalize(distance, min_distance, max_distance, 25, 300) for name, distance in raw_distances.items()}

        return normalized_radii, normalized_distances

    def create_objects_modified(self):
        self.planets_list = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
        self.planets_textures = ["textures/mercury.jpg", 
                            "textures/venus.jpg",
                            "textures/earth.jpg",
                            "textures/mars.jpg",
                            "textures/jupiter.jpg",
                            "textures/saturn.jpg",
                            "textures/uranus.jpg",
                            "textures/neptune.jpg"]
        self.satellites_textures = {"Earth": "textures/satellites/moon.jpg",
                               "Mars":  "textures/satellites/phobos.jpg",
                               "Jupiter": "textures/satellites/europa.jpg",
                               "Saturn": "textures/satellites/titan.jpg",
                               "Uranus": "textures/satellites/ariel.jpg",
                               "Neptune": "textures/satellites/triton.jpg"}
        
        self.planets_data = self.obtain_data_planets()
        radius_objects, distance_objects = self.radius_distance_objects()

        #! IMPORTANT ANNOTATION:
        ### MODE 1 - Visualització realista ###
        # Radius, distance: UA
        # Escalat: x1 

        # Crear Sol
        self.objects.append(Sun(
            self,
            [sh.vertex_shader_SUN, sh.fragment_shader_SUN],
            "textures/sun.jpg",
            [radius_objects["Sun"], 15, 15], 
        ))

        # Llista de planetes i òrbites
        for planet, texture in zip(self.planets_list, self.planets_textures):
            self.objects.append(Planet(
                self,
                [sh.vertex_shader_PLANET, sh.fragment_shader_PLANET],
                texture,
                [radius_objects[planet], 15, 15],
                glm.vec3(1, 1, 1), 
                glm.vec3(distance_objects[planet], 0, distance_objects[planet]),
                self.planets_data[planet].data["Orbital Velocity (km/s)"]/100,
                self.planets_data[planet].data["Orbital Inclination (degrees)"],
                self.planets_data[planet].data["Orbital Eccentricity"],
            ))

            self.orbits.append(Orbit(
                self,
                [sh.vertex_shader_ELLIPSE, sh.fragment_shader_ELLIPSE],
                texture,
                [radius_objects[planet], 15, 15], 
                glm.vec3(distance_objects[planet], 0, distance_objects[planet]),
                self.planets_data[planet].data["Orbital Eccentricity"]
            ))

        satellites_reader = Reader.read_satellites("data/satellites_modified.csv") 
        for index, row in satellites_reader.data.iterrows():
            name = row['name']
            planet = row['planet']
            planet_distance = distance_objects[planet]
            distance = row['Distance (10^6km)'] 
            velocity = row['Velocity (km/s)']
            texture = self.satellites_textures[planet]

            # Quan més lluny del planeta serà més asimétric 
            self.objects.append(Satellite(
                self,
                [sh.vertex_shader_PLANET, sh.fragment_shader_PLANET],
                texture,
                [radius_objects[name], 15, 15],
                glm.vec3(1, 1, 1),
                glm.vec3(planet_distance, 0, planet_distance),
                (distance/ua_conversion) +  radius_objects[planet],
                self.planets_data[planet].data["Orbital Velocity (km/s)"]/100,
                velocity*1e5,
                self.planets_data[planet].data["Orbital Inclination (degrees)"],
                self.planets_data[planet].data["Orbital Eccentricity"],
            ))

             # stars
        star_reader = Reader.read_stars("data/hygdata_v41.csv")
        self.stars = star_reader.make_stars(StarBatch, [self, [sh.vertex_shader_STAR, sh.fragment_shader_STAR], "textures/earth.jpg", "None"]) #Won't put a texture
            

    def check_events(self):
        """Funcionalitat per controlar els events durant el temps de vida del programa.
        """
        self.button_manager.check_hover(pg.mouse.get_pos())

        for event in pg.event.get():
            if event.type == pg.QUIT or (
                    event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            ):
                self.end()

            if event.type == pg.KEYDOWN and event.key == pg.K_p:
                self.ellipse = not self.ellipse
                    
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
        
        for orbit in self.orbits:
            orbit.destroy()

        # self.stars.destroy()

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

        self.stars.render()
        
        if self.ellipse:
            for orbit in self.orbits:
                orbit.render()

        # TODO: Are stars that can't be seen being processed/rendered?
        # self.stars.render()
 
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
