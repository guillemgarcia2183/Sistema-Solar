import json
import pygame as pg
import moderngl as mgl
import glm
import sys

from camera import Camera
from light import Light
from axis import Axis
from object import Sun, Planet
import shaders as sh
from gui import ButtonManager


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

        with open("gui_layout.json", "r") as file:
            gui_layout = json.load(file)

        self.button_manager.batch_add_buttons(gui_layout)

        # axis
        # self.objects.append(Axis(self))

        # planetes

        # Opcions exemple per crear l'esfera: ["stripes", 1.0, 20, 20] o bé
        # ["octahedron", 2]
        info_sphere = ["octahedron", 3]

        self.objects.append(Sun(
            self,
            [sh.vertex_shader_SUN, sh.fragment_shader_SUN],
            ["stripes", 1.25, 20, 20],
        ))

        self.objects.append(Planet(
            self,
            [sh.vertex_shader_EARTH, sh.fragment_shader_EARTH],
            info_sphere,
            # la Terra. color, size i posició son els de la Terra by default
            # (de moment)
            glm.vec3(0, 0, 1),
            glm.vec3(0.5, 0.5, 0.5),
            glm.vec3(4, 0, 4)
        ))

        # self.objects.append(Planet(
        #     self,
        #     [sh.vertex_shader_EARTH, sh.fragment_shader_EARTH],
        #     info_sphere,
        #     glm.vec3(1, 1, 1),
        #     glm.vec3(0.3, 0.3, 0.3),
        #     glm.vec3(0, 0, 8)
        # ))  # la Lluna

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
            
            # Mouse button released
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    self.camera.left_button_held = False
            
            # Mouse movement
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

