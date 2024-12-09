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

from .empty import Empty
from .text_label import TextLabel


class Text():

    __slots__ = (
        "__app",
        "__background_color"
        "__height",
        "__is_hidden",
        "__is_hovered",
        "__is_locked",
        "__shader_programs",
        "__text",
        "__uuid",
        "__vao",
        "__vertexes",
        "__width",
        "__vbo",
        "__x",
        "__y",
    )

    def __init__(self, app, uuid: str, **kwargs):
        default_kwargs = {
            "x": 0,
            "y": 0,
            "width": 1,
            "height": 1,
            "background_color": (1.0, 1.0, 1.0),
            "hidden": False,
            "locked": False,
            "text": None,
        }

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        # Engine
        self.__app = app

        # Button's unique id
        self.__uuid = uuid

        if self.__app.DEBUG:
            print(kwargs)

        # Position information
        self.__x = kwargs["x"]
        self.__y = kwargs["y"]
        self.__width = kwargs["width"]
        self.__height = kwargs["height"]

        # Color information
        self.__background_color = kwargs["background_color"]

        # States information
        self.__is_hidden = kwargs["hidden"]
        self.__is_hovered = False
        self.__is_locked = kwargs["locked"]

        # Text
        if kwargs['text'] is None:
            self.__text = Empty()
        else:
            kwargs['text'] = kwargs['text'] | {"x": self.__x, "y": self.__y}
            if self.__app.DEBUG:
                print(kwargs['text'])
            self.__text = TextLabel(
                self.__app,
                self.__uuid + "_text",
                **kwargs['text'],
            )

        # Write the shader
        self.__set_shader_programs()

        # Create all ModernGL objects
        self.__set_vao()

    @property
    def __color(self):
        return self.__shader_programs['in_colour'].value

    @__color.setter
    def __color(self, new_color):
        self.__shader_programs['in_colour'].value = new_color

    def __set_shader_programs(self):
        self.__shader_programs = self.__app.ctx.program(
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

    def __set_vao(self):

        self.__set_vbo()

        self.__vao = self.__app.ctx.vertex_array(
            self.__shader_programs, [(self.__vbo, '3f', 'in_vert')])

    def __set_vbo(self):

        self.__set_vertexes()

        self.__vbo = self.__app.ctx.buffer(self.__vertexes.tobytes())

    def __set_vertexes(self):

        # Vertex data (rectangle for the button)
        gl_x = (
            2 * (
                (
                    self.__x - (self.__width / 2) -
                    (self.__app.WIN_SIZE[0] / 2)
                ) / (
                    self.__app.WIN_SIZE[0]
                )
            ),
            2 * (
                (
                    self.__x + (self.__width / 2) -
                    (self.__app.WIN_SIZE[0] / 2)
                ) / (
                    self.__app.WIN_SIZE[0]
                )
            )
        )

        gl_y = (
            -2 * (
                (
                    self.__y - (self.__height / 2) -
                    (self.__app.WIN_SIZE[1] / 2)
                ) / (
                    self.__app.WIN_SIZE[1]
                )
            ),
            -2 * (
                (
                    self.__y + (self.__height / 2) -
                    (self.__app.WIN_SIZE[1] / 2)
                ) / (
                    self.__app.WIN_SIZE[1]
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

    @property
    def background_color(self) -> tuple[float, float, float]:
        return self.__background_color

    @background_color.setter
    def background_color(self, new_background_color: tuple[float, float, float]):
        self.__default_color = new_background_color

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
        if self.__is_locked or self.__is_hidden:
            return False

        # Get mouse coordinates
        mx, my = mouse_position

        # Return True if button is clicked
        return self.__containing(mx, my)

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
        if self.__is_locked or self.__is_hidden:
            return None

        # Get mouse coordinates
        mx, my = mouse_position

        # Update hover state
        self.__is_hovered = self.__containing(mx, my)

    def destroy(self) -> None:
        self.__vbo.release()

        self.__vao.release()

        self.__shader_programs.release()

    @property
    def height(self) -> int:
        return self.__height

    @height.setter
    def height(self, new_height: int):
        self.__height = new_height

        self.__set_vao()

    def hide(self):
        self.__is_hidden = True

    @property
    def is_hidden(self):
        return self.__is_hidden

    def render(self) -> None:
        if self.__is_hidden:
            return None

        # Render text
        self.__text.render()

        # Render backgound (draw quad as two triangles)
        self.__vao.render(mgl.TRIANGLE_STRIP)

    def unhide(self):
        self.__is_hidden = False

    @property
    def uuid(self) -> str:
        return self.__uuid

    @property
    def width(self) -> int:
        return self.__width

    @width.setter
    def width(self, new_width: int):
        self.__width = new_width

        self.__set_vao()

    @property
    def x(self) -> int:
        return self.__x

    @x.setter
    def x(self, new_x: int):
        self.__x = new_x

        self.__set_vao()

    @property
    def y(self) -> int:
        return self.__y

    @y.setter
    def y(self, new_y: int):
        self.__y = new_y

        self.__set_vao()
