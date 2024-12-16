# -*- coding: utf-8 -*- noqa

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


import moderngl as mgl
import numpy as np

from .element import Element


class Slider(Element):
    __slots__ = (
        "__current_slice",
        "__height",
        "__handle_color",
        "__handle_values",
        "__handle_vao",
        "__handle_vbo",
        "__handle_vertices",
        "__is_dragging",
        "__min_value",
        "__max_value",
        "__shader_programs",
        "__slices",
        "__track_color",
        "__track_vao",
        "__track_vbo",
        "__track_vertices",
        "__width",
        "__x",
        "__y",
    )

    def __init__(self, app, uuid: str, **kwargs):
        """    # Previous version:
        default_kwargs = {'x': 0, 'y': 0, 'width': 0, 'height': 0,
                          'min_value': 0, 'max_value': 4, 'initial_value': 2, 'track_color': (0.8, 0.8, 0.8),
                          'handle_color': (0.5, 0.5, 0.5), 'hover_color': (0.6, 0.6, 0.6), "is_hidden": False}

        kwargs = {**default_kwargs, **kwargs}

        self.app = app
        self.uuid = uuid

        # Extract general slider attributes
        self.x = kwargs["x"]
        self.y = kwargs["y"]
        self.width = kwargs["width"]
        self.height = kwargs["height"]
        self.slices = kwargs["slices"]

        # Extract slider range and initial value
        self.min_value = kwargs["min_value"]
        self.max_value = kwargs["max_value"]

        # Extract colors
        self.track_color = kwargs["track_color"]
        self.handle_color = kwargs["handle_color"]
        self.hover_color = kwargs["hover_color"]

        # Interaction states
        self.is_hovered = False
        self.is_dragging = False
        self.__is_hidden = kwargs["is_hidden"]

        dif = self.max_value - self.min_value
        self.handle_values = [self.min_value + i*dif /
                              (self.slices-1) for i in range(self.slices)]
        self.current_slice = self.slices//2
        # OpenGL setup
        self.shader_programs = self.__create_shader_programs()
        self.track_vao = self.__create_track_vao()
        self.handle_vao = self.__create_handle_vao()"""
        self._set_attributes(app, uuid, **kwargs)
        # Write the shader
        self._set_shader_programs()
        # Create all ModernGL objects
        self._set_track_vao()
        self._set_handle_vao()

    def _containing(self, mx, my):
        handle_x = self._value_to_position()
        return abs(mx - handle_x) <= self.__width / 2 and abs(my - self.__y) <= self.__height / 2

    def _set_attributes(self, app, uuid: str, **kwargs):
        """
        Set attributes only without the initialization logic.

        Parameters
        ----------
        app : TYPE
            The GraphicsEngine instance.
        uuid : string
            Unique identifier for the menu.
        **kwargs : Optional[dict[str, Any]]
            Dictionary containing menu layout and button properties.

        Returns
        -------
        None.

        """
        super().__init__(app, uuid, **kwargs)

        default_kwargs = {
            'x': 0,
            'y': 0,
            'width': 0,
            'height': 0,
            'min_value': 0,
            'max_value': 4,
            'track_color': (0.8, 0.8, 0.8),
            'handle_color': (0.5, 0.5, 0.5)}

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        if self.app.DEBUG:
            print("Button")
            print(kwargs)

        # General information
        self.__x = kwargs["x"]
        self.__y = kwargs["y"]
        self.__width = kwargs["width"]
        self.__height = kwargs["height"]
        self.__slices = kwargs["slices"]
        self.__current_slice = self.__slices//2
        self.__is_dragging = False
        # Values associated to its range
        self.__min_value = kwargs["min_value"]
        self.__max_value = kwargs["max_value"]
        dif = self.__max_value - self.__min_value
        self.__handle_values = [self.__min_value + i*dif /
                                (self.__slices-1) for i in range(self.__slices)]
        # Color information
        self.__track_color = kwargs["track_color"]
        self.__handle_color = kwargs["handle_color"]

    def _set_shader_programs(self):
        """
        Set the shader program.

        Returns
        -------
        None.

        """
        self.__shader_programs = self.app.ctx.program(
            vertex_shader='''
            #version 330
            layout (location = 0) in vec3 in_vert;
            void main() {
                gl_Position = vec4(in_vert, 1.0);
            }
            ''',
            fragment_shader='''
            #version 330
            uniform vec3 in_color;
            out vec4 frag_color;
            void main() {
                frag_color = vec4(in_color, 1.0);
            }
            '''
        )

        if self.app.DEBUG:
            print("Shader program compiled and linked successfully.")

    def _set_track_vao(self):
        self._set_track_vbo()
        self.__track_vao = self.app.ctx.vertex_array(
            self.__shader_programs, [(self.__track_vbo, '3f', 'in_vert')])

    def _set_handle_vao(self):
        self._set_handle_vbo()
        self.__handle_vao = self.app.ctx.vertex_array(
            self.__shader_programs, [(self.__handle_vbo, '3f', 'in_vert')])

    def _set_track_vbo(self):
        self._set_track_vertices()
        self.__track_vbo = self.app.ctx.buffer(self.__track_vertices.tobytes())

    def _set_handle_vbo(self):
        self._set_handle_vertices()
        self.__handle_vbo = self.app.ctx.buffer(
            self.__handle_vertices.tobytes())

    def _set_track_vertices(self):
        gl_x = (
            2 * ((self.__x - (self.__width / 2) -
                 (self.app.WIN_SIZE[0] / 2) - self.__width / self.__slices) / (self.app.WIN_SIZE[0])),
            2 * ((self.__x + (self.__width / 2) -
                 (self.app.WIN_SIZE[0] / 2) + self.__width / self.__slices) / (self.app.WIN_SIZE[0]))
        )

        gl_y = (
            -2 * ((self.__y - (self.__height / 2) -
                  (self.app.WIN_SIZE[1] / 2)) / (self.app.WIN_SIZE[1])),
            -2 * ((self.__y + (self.__height / 2) -
                  (self.app.WIN_SIZE[1] / 2)) / (self.app.WIN_SIZE[1]))
        )

        self.__track_vertices = np.array(
            [
                gl_x[0], gl_y[0], 0.0,
                gl_x[1], gl_y[0], 0.0,
                gl_x[0], gl_y[1], 0.0,
                gl_x[1], gl_y[1], 0.0,
            ],
            dtype='f4'
        )

    def _set_handle_vertices(self):
        handle_x = self._value_to_position()
        gl_x = (
            2*((handle_x - self.__width / self.__slices) -
               self.app.WIN_SIZE[0] / 2) / (self.app.WIN_SIZE[0]),
            2*((handle_x + self.__width / self.__slices) -
               self.app.WIN_SIZE[0] / 2) / (self.app.WIN_SIZE[0])
        )

        gl_y = (
            -2*((self.__y - self.__height / 2) -
                self.app.WIN_SIZE[1] / 2) / (self.app.WIN_SIZE[1]),
            -2*((self.__y + self.__height / 2) -
                self.app.WIN_SIZE[1] / 2) / (self.app.WIN_SIZE[1])
        )

        self.__handle_vertices = np.array(
            [
                gl_x[0], gl_y[0], 0.0,
                gl_x[1], gl_y[0], 0.0,
                gl_x[0], gl_y[1], 0.0,
                gl_x[1], gl_y[1], 0.0,
            ],
            dtype='f4'
        )

    def _value_to_position(self):
        """
        Map a slider value to a screen position.
        """
        return self.__x - self.__width / 2 + (self.__handle_values[self.__current_slice] - self.__min_value) / (self.__max_value - self.__min_value) * self.__width

    def check_hover(self, mouse_position: tuple[int, int]):
        pass

    def is_hovered(self):
        pass

    def toggle(self):
        pass

    def untoggle(self):
        pass

    def render(self):
        """
        Render the slider.
        """
        if self.is_hidden:
            return None
        # Render handle
        self.__shader_programs['in_color'].value = self.__handle_color
        self.__handle_vao.render(mgl.TRIANGLE_STRIP)

        # Render track
        self.__shader_programs['in_color'].value = self.__track_color
        self.__track_vao.render(mgl.TRIANGLE_STRIP)

    def destroy(self) -> None:
        self.__handle_vao.release()

        self.__track_vao.release()

        self.__shader_programs.release()

    def check_click(self, mouse_position):
        """
        Check if the slider is clicked and begin dragging if necessary.
        """
        if self.is_locked or self.is_hidden:
            return None
        mx, my = mouse_position
        if self._containing(mx, my):
            self.__is_dragging = True

    def check_motion(self, mouse_position: tuple[int, int]):
        if self.is_locked or self.is_hidden:
            return None
        mx, my = mouse_position

        if self._containing(mx, my):
            if self.__is_dragging:
                value = self.update_value(mx)
                return self.uuid + ":" + str(value)

        return None

    def check_unclick(self, mouse_position):
        if self.is_locked or self.is_hidden:
            return None

        self.__is_dragging = False
        return self.uuid

    def update_value(self, mouse_x):
        """
        Update the slider value based on mouse x position.
        """
        new_value = self.__min_value + \
            (mouse_x - (self.__x - self.__width / 2)) / \
            self.__width * (self.__max_value - self.__min_value)
        self.__current_slice = min(range(len(self.__handle_values)), key=lambda i: abs(
            self.__handle_values[i] - new_value))
        self._set_handle_vao()

        return self.__handle_values[self.__current_slice]

    def release(self):
        """
        Stop dragging when mouse button is released.
        """
        self.__is_dragging = False
