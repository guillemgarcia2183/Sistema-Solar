# -*- coding: utf-8 -*- noqa
"""
Created on Thu Oct 17 12:06:14 2024

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


class RectangularButton(Element):

    __slots__ = (
        "__app",
        "__default_color",
        "__height",
        "__hover_color",
        "__is_hidden",
        "__is_hovered",
        "__is_locked",
        "__locked_color",
        "__shader_programs",
        "__text",
        "__uuid",
        "__vao",
        "__vbo",
        "__vertexes",
        "__width",
        "__x",
        "__y",
    )

    def __init__(self, app, uuid: str, **kwargs):
        default_kwargs = {
            "x": 0,
            "y": 0,
            "width": 1,
            "height": 1,
            "default_color": (1.0, 1.0, 1.0),
            "hover_color": None,
            "locked_color": None,
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
        self.__default_color = kwargs["default_color"]

        if kwargs["hover_color"] is None:
            self.__hover_color = kwargs["default_color"]
        else:
            self.__hover_color = kwargs["hover_color"]

        if kwargs["locked_color"] is None:
            self.__locked_color = kwargs["default_color"]
        else:
            self.__locked_color = kwargs["locked_color"]

        # States information
        self.__is_hidden = kwargs["hidden"]
        self.__is_hovered = False
        self.__is_locked = kwargs["locked"]

        # Text on the button
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

    def __containing(self, pos_x, pos_y):
        return (
            self.__x - self.__width / 2 <= pos_x <= self.__x + self.__width / 2
        ) and (
            self.__y - self.__height / 2 <= pos_y <= self.__y + self.__height / 2
        )

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

    def _calculate_state(self):
        # Set color based on state
        if self.__is_locked:
            self.color = self.__locked_color
        elif self.__is_hovered:
            self.color = self.__hover_color
        else:
            self.color = self.__default_color

    def _render(self):
        # Render possible text on button
        self.__text.render()

        # Render button (draw quad as two triangles)
        self.__vao.render(mgl.TRIANGLE_STRIP)

    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        # Cannot be clicked if is locked
        if self.__is_locked or self.__is_hidden:
            return False

        # Get mouse coordinates
        mx, my = mouse_pos

        # Return True if button is clicked
        return self.__containing(mx, my)

    def check_hover(self, mouse_pos: tuple[int, int]) -> None:
        # Cannot be hovered if is locked
        if self.__is_locked or self.__is_hidden:
            return None

        # Get mouse coordinates
        mx, my = mouse_pos

        # Update hover state
        self.__is_hovered = self.__containing(mx, my)

    @property
    def color(self) -> tuple[float, float, float]:
        return self.__shader_programs['in_colour'].value

    @color.setter
    def color(self, new_color: tuple[float, float, float]):
        self.__shader_programs['in_colour'].value = new_color

    @property
    def default_color(self) -> tuple[float, float, float]:
        return self.__default_color

    @default_color.setter
    def default_color(self, new_default_color: tuple[float, float, float]):
        self.__default_color = new_default_color

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
    def hover_color(self) -> tuple[float, float, float]:
        return self.__hover_color

    @hover_color.setter
    def hover_color(self, new_hover_color: tuple[float, float, float]):
        self.__hover_color = new_hover_color

    @property
    def is_hidden(self):
        return self.__is_hidden

    @property
    def is_locked(self):
        return self.__is_locked

    def lock(self):
        self.__is_locked = True

    @property
    def locked_color(self) -> tuple[float, float, float]:
        return self.__locked_color

    @locked_color.setter
    def locked_color(self, new_locked_color: tuple[float, float, float]):
        self.__locked_color = new_locked_color

    def render(self) -> None:
        if self.__is_hidden:
            return None

        self._calculate_state()

        self._render()

    def unhide(self):
        self.__is_hidden = False

    def unlock(self):
        self.__is_locked = True

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
