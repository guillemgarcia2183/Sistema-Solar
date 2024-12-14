# -*- coding: utf-8 -*- noqa
"""
Created on Sun Dec  8 15:51:26 2024

@author: Joel Tapia Salvador
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


import moderngl as mgl
import numpy as np

from .element import Element
from .empty import Empty
from .text_label import TextLabel


class Text(Element):

    __slots__ = (
        "__background_color",
        "__height",
        "__is_hovered",
        "__shader_programs",
        "__text",
        "__vao",
        "__vbo",
        "__vertexes",
        "__width",
        "__x",
        "__y",
    )

###############################################################################
#                             Overloaded Operators                            #

    def __init__(self, app, uuid: str, **kwargs):
        # Inicialize attributes
        self._set_attributes(app, uuid, **kwargs)

        # Write the shader
        self._set_shader_programs()

        # Create all ModernGL objects
        self._set_vao()

###############################################################################


###############################################################################
#                              Protected Methods                              #


    def __calculate_state(self):  # noqa
        self.color = self.__background_color

###############################################################################


###############################################################################
#                               Private Methods                               #

    def _containing(self, pos_x, pos_y):  # noqa
        return (
            self.x - self.width / 2 <= pos_x <= self.x + self.width / 2
        ) and (
            self.y - self.height / 2 <= pos_y <= self.y + self.height / 2
        )

    def _render(self):
        # Render text
        self.__text.render()

        # Render backgound (draw quad as two triangles)
        self.__vao.render(mgl.TRIANGLE_STRIP)

    def _set_attributes(self, app, uuid: str, **kwargs):
        super().__init__(app, uuid, **kwargs)

        default_kwargs = {
            "x": 0,
            "y": 0,
            "width": 1,
            "height": 1,
            "background_color": (1.0, 1.0, 1.0),
            "text": None,
        }

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        if self.app.DEBUG:
            print("Text")
            print(kwargs)

        # Position information
        self.__x = kwargs["x"]
        self.__y = kwargs["y"]
        self.__width = kwargs["width"]
        self.__height = kwargs["height"]

        # Color information
        self.__background_color = kwargs["background_color"]

        # States information
        self.__is_hovered = False

        # Text
        if kwargs['text'] is None:
            kwargs['text'] = {
                'text': "",
                'x': 0,
                'y': 0,
                'color': (0.0, 0.0, 0.0),
                'sys_font': 'Arial',
                'font_size': 1,
                'scale_factor': 1,
            }

        kwargs['text'] = kwargs['text'] | {"x": self.x, "y": self.y}

        if self.app.DEBUG:
            print(kwargs['text'])

        self.__text: TextLabel = TextLabel(
            self.app,
            self.uuid + "_text_label",
            **kwargs['text'],
        )

    def _set_shader_programs(self):
        self.__shader_programs = self.app.ctx.program(
            vertex_shader='''
            #version 330

            layout (location = 0) in vec3 in_vert;

            uniform vec3 in_colour;

            out vec3 frag_color;

            void main() {
                frag_color = in_colour;
                gl_Position = vec4(in_vert, 1.0);
            }
            ''',
            fragment_shader='''
            #version 330

            in vec3 frag_color;

            out vec4 f_color;

            void main() {
                f_color = vec4(frag_color, 1.0);
            }
            '''
        )

    def _set_vao(self):

        self._set_vbo()

        self.__vao = self.app.ctx.vertex_array(
            self.__shader_programs, [(self.__vbo, '3f', 'in_vert')])

    def _set_vbo(self):

        self._set_vertexes()

        self.__vbo = self.app.ctx.buffer(self.vertexes.tobytes())

    def _set_vertexes(self):

        # Vertex data (rectangle for the button)
        gl_x = (
            2 * (
                (
                    self.x - (self.width / 2) -
                    (self.app.WIN_SIZE[0] / 2)
                ) / (
                    self.app.WIN_SIZE[0]
                )
            ),
            2 * (
                (
                    self.x + (self.width / 2) -
                    (self.app.WIN_SIZE[0] / 2)
                ) / (
                    self.app.WIN_SIZE[0]
                )
            )
        )

        gl_y = (
            -2 * (
                (
                    self.y - (self.__height / 2) -
                    (self.app.WIN_SIZE[1] / 2)
                ) / (
                    self.app.WIN_SIZE[1]
                )
            ),
            -2 * (
                (
                    self.y + (self.height / 2) -
                    (self.app.WIN_SIZE[1] / 2)
                ) / (
                    self.app.WIN_SIZE[1]
                )
            )
        )

        self.__vertexes = np.array(
            [
                gl_x[0], gl_y[0], 0.0,
                gl_x[1], gl_y[0], 0.0,
                gl_x[0], gl_y[1], 0.0,
                gl_x[1], gl_y[1], 0.0,
            ],
            dtype='f4'
        )

###############################################################################


###############################################################################
#                                Public Methods                               #


    def check_click(self, mouse_position: tuple[int, int]) -> bool:
        """
        Check if a click has been on the button,

        Parameters
        ----------
        mouse_position : Tuple[int, int]
            Position of the mouse, tuple of integers (pixels) x, y.

        Returns
        -------
        bool
            If the click has been on the button.

        """
        # Cannot be clicked if is locked
        if self.is_locked or self.is_hidden:
            return None

        # Get mouse coordinates
        mx, my = mouse_position

        # Return True if button is clicked
        if self._containing(mx, my):
            return self.uuid

    def check_hover(self, mouse_position: tuple[int, int]):
        """
        Check if the mouse is hovering on top of the button.

        Parameters
        ----------
        mouse_position : Tuple[int, int]
            Position of the mouse, tuple of integers (pixels) x, y.

        Returns
        -------
        None.

        """
        # Cannot be hovered if is locked
        if self.is_locked or self.is_hidden:
            return None

        # Get mouse coordinates
        mx, my = mouse_position

        # Update hover state
        self.__is_hovered = self._containing(mx, my)

    def check_time(self, delta):
        pass

    def destroy(self) -> None:
        self.__vbo.release()

        self.__vao.release()

        self.__shader_programs.release()

    def render(self) -> None:
        if self.is_hidden:
            return None

        self.__calculate_state()

        self._render()

    def toggle(self):
        return None

    def untoggle(self):
        return None

###############################################################################


###############################################################################
#                                  Properties                                 #


    @property  # noqa
    def background_color(self) -> tuple[float, float, float]:
        return self.__background_color

    @background_color.setter
    def background_color(self, new_background_color: tuple[float, float, float]):
        self.__default_color = new_background_color

    @property
    def color(self):
        return self.__shader_programs['in_colour'].value

    @color.setter
    def color(self, new_color):
        self.__shader_programs['in_colour'].value = new_color

    @property
    def font(self) -> str:
        return self.__text.font

    @font.setter
    def font(self, new_font: str):
        self.__text.font = new_font

    @property
    def font_size(self) -> int:
        return self.__text.font_size

    @font_size.setter
    def font_size(self, new_font_size: int):
        self.__text.font_size = new_font_size

    @property
    def height(self) -> int:
        return self.__height

    @height.setter
    def height(self, new_height: int):
        self.__height = new_height

        self._set_vao()

    @property
    def is_hovered(self) -> bool:
        return self.__is_hovered

    @property
    def scale_factor(self) -> int:
        return self.__text.scale_factor

    @scale_factor.setter
    def scale_factor(self, new_scale_factor: int):
        self.__text.scale_factor = new_scale_factor

    @property
    def text_color(self) -> tuple[float, float, float]:
        return self.__text.text_color

    @text_color.setter
    def text_color(self, new_color: tuple[float, float, float]):
        self.__text.text_color = new_color

    @property
    def vertexes(self):
        return self.__vertexes

    @property
    def width(self) -> int:
        return self.__width

    @width.setter
    def width(self, new_width: int):
        self.__width = new_width

        self._set_vao()

    @property
    def x(self) -> int:
        return self.__x

    @x.setter
    def x(self, new_x: int):
        self.__x = new_x

        self.__text.x = new_x

        self._set_vao()

    @property
    def y(self) -> int:
        return self.__y

    @y.setter
    def y(self, new_y: int):
        self.__y = new_y

        self.__text.y = new_y

        self._set_vao()

###############################################################################
