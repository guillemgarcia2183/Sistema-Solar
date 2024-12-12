# -*- coding: utf-8 -*- noqa
"""
Created on Wed Dec 11 22:38:48 2024

@author: Joel Tapia Salvador
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


import moderngl as mgl

from .element import Element
from .empty import Empty
from .text_label import TextLabel


class Button(Element):

    __slots__ = (
        "__app",
        "__default_color",
        "__hover_color",
        "__is_hidden",
        "__is_hovered",
        "__is_locked",
        "__locked_color",
        "__radius",
        "__shader_programs",
        "__text",
        "__uuid",
        "__vao",
        "__vbo",
        "__vertexes",
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

    def __calculate_state(self):
        # Set color based on state
        if self.is_locked:
            self.color = self.locked_color
        elif self.is_hovered:
            self.color = self.hover_color
        else:
            self.color = self.default_color

###############################################################################


###############################################################################
#                               Private Methods                               #

    def _containing(self, pos_x, pos_y) -> bool:
        raise NotImplementedError

    def _render(self):
        # Render possible text on button
        self.__text.render()

        # Render button (draw quad as two triangles)
        self.__vao.render(mgl.TRIANGLE_STRIP)

    def _set_attributes(self, app, uuid: str, **kwargs):
        default_kwargs = {
            "x": 0,
            "y": 0,
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
            print("Button")
            print(kwargs)

        # Position information
        self.__x = kwargs["x"]
        self.__y = kwargs["y"]

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

    def _set_shader_programs(self):
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

        if self.__app.DEBUG:
            print("Shader program compiled and linked successfully.")

    def _set_vao(self):

        self._set_vbo()

        self.__vao = self.__app.ctx.vertex_array(
            self.__shader_programs, [(self.__vbo, '3f', 'in_vert')])

    def _set_vbo(self):

        self._set_vertexes()

        self.__vbo = self.__app.ctx.buffer(self.vertexes.tobytes())

    def _set_vertexes(self):
        raise NotImplementedError

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
            return False

        # Get mouse coordinates
        mx, my = mouse_position

        # Return True if button is clicked
        return self._containing(mx, my)

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

    def destroy(self):
        self.__vbo.release()

        self.__vao.release()

        self.__shader_programs.release()

    def hide(self):
        self.__is_hidden = True

    def lock(self):
        self.__is_locked = True

    def render(self):
        if self.is_hidden:
            return None

        self.__calculate_state()

        self._render()

    def unhide(self):
        self.__is_hidden = False

    def unlock(self):
        self.__is_locked = True

###############################################################################


###############################################################################
#                                  Properties                                 #

    @property
    def color(self) -> tuple[float, float, float]:
        return self.__shader_programs['in_colour'].value

    @color.setter
    def color(self, new_color: tuple[float, float, float]):
        self.__shader_programs['in_colour'].value = new_color

    @property
    def default_color(self) -> tuple[float, float, float]:
        """
        Property of default color of the button.

        Returns
        -------
        Tuple[float, float, float]
            Tuple of float values of color RGB (0-1).

        """
        return self.__default_color

    @default_color.setter
    def default_color(self, new_default_color: tuple[float, float, float]):
        self.__default_color = new_default_color

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
    def is_hovered(self):
        return self.__is_hovered

    @property
    def is_locked(self):
        return self.__is_locked

    @property
    def locked_color(self) -> tuple[float, float, float]:
        return self.__locked_color

    @locked_color.setter
    def locked_color(self, new_locked_color: tuple[float, float, float]):
        self.__locked_color = new_locked_color

    @property
    def uuid(self) -> str:
        return self.__uuid

    @property
    def vertexes(self):
        raise NotImplementedError

    @property
    def x(self) -> int:
        return self.__x

    @x.setter
    def x(self, new_x: int):
        self.__x = new_x

        self._set_vao()

    @property
    def y(self) -> int:
        return self.__y

    @y.setter
    def y(self, new_y: int):
        self.__y = new_y

        self._set_vao()

###############################################################################
