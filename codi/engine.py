import json
import pygame as pg
import moderngl as mgl
import glm
import sys
# from axis import Axis
from camera import Camera, FollowCamera
from light import Light
from objects import *
from reader import Reader
from gui import ButtonManager
import shaders as sh

### VARIABLES GLOBALS ###
UA_CONVERSION = 149_600_000  # 1 UA en kilómetros

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
        "planets_data",
        "aux_objects",
        "aux_orbits",
        "second_cam"
    )

    def __init__(self, fs=True, win_size=(1200, 800)):
        """Inicialització de la classe GraphicsEngine

        Args:
            fs (bool, optional): Si es True, s'executa en full screen. Defaults to True
            win_size (tuple, optional): Tamany de finestra de l'aplicació. Defaults to (900,800).
        """
        # init pygame modules
        pg.init()
        # window size
        if fs:  # Fullscreen windowed if enabled
            screen_sizes = pg.display.get_desktop_sizes()
            primary_screen_size = screen_sizes[0]
            self.WIN_SIZE = (primary_screen_size[0], primary_screen_size[1]-50)
        else:  # Input window size
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
        # Distància arbitrària, de moment.
        # TODO: que la classe calculi una distància entre la superfície del planeta i el seu satèl·lit més proper
        # Per a la presentació, habilitar les diferents càmeres
        self.second_cam = FollowCamera(self, 0.5)
        # light
        self.light = Light()

        self.objects = []
        self.orbits = []

        self.aux_objects = []  # 2n mode
        self.aux_orbits = []  # 2n mode

        self.clock = pg.time.Clock()
        self.time = 0

        # gui
        self.button_manager = ButtonManager(self)

        # with open(r"./codi/gui_layout.json", "r") as file:
        #     gui_layout = json.load(file)

        with open("gui_layout.json", "r") as file:
            gui_layout = json.load(file)

        self.button_manager.batch_add_buttons(gui_layout)

        self.create_objects()
        # axis
        # self.objects.append(Axis(self))

        # Establim un target a la càmera. Això hauria d'estar al check_events
        # Aquesta línia saltarà error si la càmera inicialitzada no és del tipus "FollowCamera"
        self.second_cam.select_target(self.objects[3])
        # Informació relacionada amb el context de l'aplicació
        self.info = "Visualització del sol"
        self.ellipse = True

    def obtain_data_planets(self):
        """Obtenció de les dades dels planetes cridant al seu dataset

        Returns:
            dict: Retornar les dades dels planetes en format diccionari
        """
        planets_data = dict()

        for planet in self.planets_list:
            read_data = Reader.read_planets("data/planets.csv", planet)
            planets_data[planet] = read_data

        return planets_data

    @staticmethod
    def normalize(value, min_value, max_value, new_min, new_max):
        """Normalització min-max, utilitzat per controlar radis i distàncies dels objectes

        Args:
            value (float): Distància o radi del objecte
            min_value (float): Valor mínim de la distància o radi
            max_value (float): Valor màxim de la distància o radi
            new_min (float): Nou valor que serà la mínima distància o radi
            new_max (float): Nou valor que serà la màxima distància o radi

        Returns:
            float: Nou valor normalitzat
        """
        # Normalización min-max
        return ((value - min_value) / (max_value - min_value)) * (new_max - new_min) + new_min

    def radius_distance_objects(self):
        """Càlcul de les distàncies i radis dels objectes

        Returns:
            (dict, dict, dict, dict): Dos diccionaris amb les distàncies i radis normalitzats, i dos diccionaris amb les distàncies i radis reals
        """
        # Radios y distancias sin escalar (en UA) para calcular valores min y max
        raw_radii = {"Sun": 696000 / UA_CONVERSION}
        raw_distances = {}

        for planet in self.planets_list:
            # Almacenar radios y distancias en UA sin normalizar
            raw_radii[planet] = (
                self.planets_data[planet].data["Diameter (km)"] / 2) / UA_CONVERSION
            # Distancia del planeta al Sol
            raw_distances[planet] = (
                self.planets_data[planet].data["Distance from Sun (10^6 km)"] * 1e6) / UA_CONVERSION

        # Satélites
        satellites_reader = Reader.read_satellites("data/satellites.csv")
        for index, row in satellites_reader.data.iterrows():
            name = row['name']
            planet = row['planet']
            # Radi del satèl·lit en UA
            raw_radii[name] = row['radius'] / UA_CONVERSION
            # Distancia del satèl·lit al Sol
            raw_distances[name] = raw_distances[planet] + \
                (row['Distance_to_planet (10^6km)']*1e6 / UA_CONVERSION)

        # Encontrar los valores mínimo y máximo para normalización
        min_radius, max_radius = min(
            raw_radii.values()), max(raw_radii.values())
        min_distance, max_distance = min(
            raw_distances.values()), max(raw_distances.values())

        # Normalizar a los rangos deseados
        normalized_radii = {name: self.normalize(
            radius, min_radius, max_radius, 0.0001, 20) for name, radius in raw_radii.items()}
        normalized_distances = {name: self.normalize(
            distance, min_distance, max_distance, 21, 500) for name, distance in raw_distances.items()}

        # print(f"normalized_distances: {normalized_distances}")

        normalized_radii_real = {name: radius *
                                 100 for name, radius in raw_radii.items()}
        normalized_distances_real = {
            name: distance*100 for name, distance in raw_distances.items()}

        return normalized_radii, normalized_distances, normalized_radii_real, normalized_distances_real

    def create_objects(self):
        """Creació dels objectes que formaràn part de l'escena
        """
        self.planets_list = ["Mercury", "Venus", "Earth",
                             "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
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
        radius_objects, distance_objects, real_radius, real_distance = self.radius_distance_objects()

        #! IMPORTANT ANNOTATION:
        ### MODE 1 - Visualització realista ###
        # Radius, distance: UA
        # Escalat: x1

        # Crear Sol
        self.objects.append(Sun(
            self,
            [sh.vertex_shader_SUN, sh.fragment_shader_SUN],
            "textures/sun.jpg",
            [radius_objects["Sun"], 25, 25],
        ))

        self.aux_objects.append(Sun(
            self,
            [sh.vertex_shader_SUN, sh.fragment_shader_SUN],
            "textures/sun.jpg",
            [real_radius["Sun"], 25, 25],
        ))

        # Llista de planetes i òrbites
        for planet, texture in zip(self.planets_list, self.planets_textures):
            self.objects.append(Planet(
                self,
                [sh.vertex_shader_PLANET, sh.fragment_shader_PLANET],
                texture,
                [radius_objects[planet], 15, 15],
                glm.vec3(1, 1, 1),
                glm.vec3(distance_objects[planet], 0,
                         distance_objects[planet]),
                self.planets_data[planet].data["Orbital Velocity (km/s)"]/100,
                self.planets_data[planet].data["Orbital Inclination (degrees)"],
                self.planets_data[planet].data["Orbital Eccentricity"],
            ))

            self.aux_objects.append(Planet(
                self,
                [sh.vertex_shader_PLANET, sh.fragment_shader_PLANET],
                texture,
                [real_radius[planet], 15, 15],
                glm.vec3(1, 1, 1),
                glm.vec3(real_distance[planet], 0, real_distance[planet]),
                self.planets_data[planet].data["Orbital Velocity (km/s)"]/100,
                self.planets_data[planet].data["Orbital Inclination (degrees)"],
                self.planets_data[planet].data["Orbital Eccentricity"],
            ))

            self.orbits.append(Orbit(
                self,
                [sh.vertex_shader_ELLIPSE, sh.fragment_shader_ELLIPSE],
                texture,
                [radius_objects[planet], 15, 15],
                glm.vec3(distance_objects[planet], 0,
                         distance_objects[planet]),
                self.planets_data[planet].data["Orbital Eccentricity"]
            ))

            self.aux_objects.append(Orbit(
                self,
                [sh.vertex_shader_ELLIPSE, sh.fragment_shader_ELLIPSE],
                texture,
                [real_radius[planet], 15, 15],
                glm.vec3(real_distance[planet], 0, real_distance[planet]),
                self.planets_data[planet].data["Orbital Eccentricity"]
            ))

        satellites_reader = Reader.read_satellites("data/satellites.csv")
        for index, row in satellites_reader.data.iterrows():
            name = row['name']
            planet = row['planet']
            velocity = row['Velocity (km/s)']
            texture = self.satellites_textures[planet]

            self.objects.append(Satellite(
                self,
                [sh.vertex_shader_PLANET, sh.fragment_shader_PLANET],
                texture,
                [radius_objects[name], 15, 15],
                glm.vec3(1, 1, 1),
                position_planet=glm.vec3(
                    distance_objects[planet], 0, distance_objects[planet]),
                position_satellite=glm.vec3(
                    distance_objects[name]+radius_objects[planet], 0, distance_objects[name]+radius_objects[planet]),
                velocity_planet=self.planets_data[planet].data[
                    "Orbital Velocity (km/s)"]/100,
                velocity_satellite=velocity,
                inclination=self.planets_data[planet].data[
                    "Orbital Inclination (degrees)"],
                eccentricity=self.planets_data[planet].data["Orbital Eccentricity"],
            ))

        # Add asteroids
        speed_asteroids = (self.planets_data["Mars"].data["Orbital Velocity (km/s)"] +
                           self.planets_data["Jupiter"].data["Orbital Velocity (km/s)"])/200
        # Main asteroid Belt
        self.objects.append(AsteroidBatch(
            self,
            [sh.vertex_shader_ASTEROID, sh.fragment_shader_ASTEROID],
            "textures/asteroids.jpg",
            [0.35, 3, 3],
            num_asteroids=225,  # Or however many you want
            distance1=distance_objects["Mars"]+25,
            distance2=distance_objects["Jupiter"]-25,
            velocity=speed_asteroids,
            eccentricity=self.planets_data["Mars"].data["Orbital Eccentricity"],
            type="Belt",
            enable_collision=True
        ))
        # Trojan Asteroids
        self.objects.append(AsteroidBatch(
            self,
            [sh.vertex_shader_ASTEROID, sh.fragment_shader_ASTEROID],
            "textures/asteroids.jpg",  # You'll need an asteroid texture
            [0.2, 5, 5],  # Adjust these parameters as needed
            num_asteroids=100,  # Or however many you want
            distance1=distance_objects["Jupiter"]+35,
            distance2=distance_objects["Jupiter"]+45,
            velocity=self.planets_data["Jupiter"].data["Orbital Velocity (km/s)"] /
            100,
            eccentricity=self.planets_data["Jupiter"].data["Orbital Eccentricity"],
            type="Trojan Right"
        ))
        self.objects.append(AsteroidBatch(
            self,
            [sh.vertex_shader_ASTEROID, sh.fragment_shader_ASTEROID],
            "textures/asteroids.jpg",  # You'll need an asteroid texture
            [0.2, 5, 5],  # Adjust these parameters as needed
            num_asteroids=100,  # Or however many you want
            distance1=distance_objects["Jupiter"]+35,
            distance2=distance_objects["Jupiter"]+45,
            velocity=self.planets_data["Jupiter"].data["Orbital Velocity (km/s)"] /
            100,
            eccentricity=self.planets_data["Jupiter"].data["Orbital Eccentricity"],
            type="Trojan Left"
        ))

        # Saturn rings
        self.objects.append(RingBatch(
            self,
            [sh.vertex_shader_RING, sh.fragment_shader_RING],
            "textures/saturn_rings.png",
            [0, 0, 0],
            planet_distance=distance_objects["Saturn"],
            ring_inner_radius=radius_objects["Saturn"] - 5,
            ring_outer_radius=radius_objects["Saturn"] - 10,
            velocity=self.planets_data["Saturn"].data["Orbital Velocity (km/s)"] /
            100,
            eccentricity=self.planets_data["Saturn"].data["Orbital Eccentricity"]
        ))

        # Implement stars
        star_reader = Reader.read_stars("data/stars.csv")
        self.stars = star_reader.make_stars(
            StarBatch,
            self,
            [sh.vertex_shader_STAR, sh.fragment_shader_STAR],
            "textures/earth.jpg",  # Won't put a texture
            [0, 0, 0],
            constellations=True,
            constellations_shaders=[
                sh.vertex_shader_CONSTELLATION, sh.fragment_shader_CONSTELLATION]
        )

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

            if event.type == pg.KEYDOWN and event.key == pg.K_k:
                self.camera, self.second_cam = self.second_cam, self.camera

            if event.type == pg.KEYDOWN and event.key == pg.K_m:
                self.objects, self.aux_objects = self.aux_objects, self.objects
                self.orbits, self.aux_orbits = self.aux_orbits, self.orbits

                # Update the view matrix
                m_view = self.camera.get_view_matrix()
                for object in self.objects:
                    object.shader['m_view'].write(m_view)
                self.stars.shader['m_view'].write(m_view)

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
                elif button_event == "elipses":
                    self.ellipse = not self.ellipse
                elif button_event == "canvi_camera":
                    print("c")
                    self.camera, self.second_cam = self.second_cam, self.camera
                elif button_event == "escala":
                    self.objects, self.aux_objects = self.aux_objects, self.objects
                    self.orbits, self.aux_orbits = self.aux_orbits, self.orbits

                    # Update the view matrix
                    m_view = self.camera.get_view_matrix()
                    for object in self.objects:
                        object.shader['m_view'].write(m_view)
                    self.stars.shader['m_view'].write(m_view)

            # Mouse button released
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    self.camera.left_button_held = False

            elif event.type == pg.MOUSEMOTION and self.camera.left_button_held:
                current_mouse_pos = pg.mouse.get_pos()
                if self.camera.last_mouse_pos is not None and not (self.camera.get_type == "FollowCamera" and self.camera.lock_target):
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
        """

        self.button_manager.destroy()

        for objecte in self.objects:
            objecte.destroy()

        for orbit in self.orbits:
            orbit.destroy()

        self.stars.destroy()

        pg.quit()
        sys.exit()

    def get_time(self):
        """Funció per obtenir el temps (en ticks) - Ús: Fer rotar objectes
        """
        self.time = pg.time.get_ticks() * 0.001

    def move(self):
        """Funció per fer moure els objectes que es troben en orbitació
        """
        for objecte in self.objects:
            objecte.move()

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
            self.move()
            self.camera.follow_target()
            self.render()
            self.clock.tick(60)
