# -*- coding: utf-8 -*- noqa
"""
Created on Thu Nov 28 12:52:06 2024

@author: Joel Tapia Salvador
"""
import json
import pygame as pg
import moderngl as mgl
import traceback
import sys

from gui import GUIManager


class TestEngine():
    """GUI Test Engine."""

    def __init__(self, debug=False, fs=True, win_size=(1200, 800)):
        """Inicialització de la classe TestEngine

        Args:
            win_size (tuple, optional): Tamany de finestra de l'aplicació. Defaults to (900,800).
        """
        self.DEBUG = debug
        # init pygame modules
        pg.init()
        pg.font.init()
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
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)

        # create opengl context
        pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.BLEND)

        if self.DEBUG:
            print(f"ModernGL Version: {self.ctx.version_code}")
            print(f"OpenGL Vendor: {self.ctx.info['GL_VENDOR']}")
            print(f"OpenGL Renderer: {self.ctx.info['GL_RENDERER']}")
            print(f"OpenGL Version: {self.ctx.info['GL_VERSION']}")
            # print(f"Shader Version: {
            #       self.ctx.info['GL_SHADING_LANGUAGE_VERSION']}")

        self.info = "Test GUI"
        pg.display.set_caption(self.info)

        self.clock = pg.time.Clock()
        self.time = 0

        self.gui = GUIManager(self)

        with open("gui_layout.json", "r") as file:
            gui_layout = json.load(file)

        self.gui.batch_add_elements(gui_layout)

    def check_events(self):
        """Funcionalitat per controlar els events durant el temps de vida del programa.
        """
        self.gui.check_hover(pg.mouse.get_pos())

        for event in pg.event.get():
            if event.type == pg.QUIT or (
                    event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            ):
                raise KeyboardInterrupt("Exit game via click.")

            if event.type == pg.MOUSEBUTTONDOWN:
                button_event = self.gui.check_click(
                    pg.mouse.get_pos())
                # if button_event == "day_picker":
                #     print("Day picker pressed.")
                # elif button_event == "zoom_in":
                #     print("Zoom in pressed.")
                # elif button_event == "zoom_out":
                #     print("Zoom out pressed.")
                # elif button_event == "constellations_visibility":
                #     print("Constelations visibility pressed.")

    def end(self):
        """
        Destruir tots els objectes i finalitzar la simulació.

        Returns
        -------
        None.

        """
        if self.DEBUG:
            print("Ending...")

        # self.button_manager.destroy()
        self.gui.destroy()

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
        # self.button_manager.render()
        self.gui.render()

        # Swap buffers + display caption
        pg.display.set_caption(self.info)
        pg.display.flip()

    def run(self):
        """Funció per corre el programa frame a frame.
        """
        while True:
            self.get_time()
            self.check_events()
            self.render()
            self.clock.tick(60)


if __name__ == "__main__":
    app = TestEngine(debug=True, fs=True)
    try:
        app.run()
    except Exception:
        print(traceback.format_exc()[
            :-1].replace("  ", "\t").replace("\n", "\n\t\t"))
    finally:  # noqa
        app.end()
