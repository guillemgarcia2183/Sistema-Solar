# -*- coding: utf-8 -*- noqa
"""
Created on Wed Dec 11 22:38:48 2024

@author: Joel Tapia Salvador
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


from abc import abstractmethod
import moderngl as mgl

from .element import Element
from .text_label import TextLabel


class Button(Element):
    """Button Element."""

    __slots__ = (
        "__default_color",
        "__hover_color",
        "__is_hovered",
        "__locked_color",
        "__radius",
        "__shader_programs",
        "__text",
        "__vao",
        "__vbo",
        "__vertexes",
        "__x",
        "__y",
    )

###############################################################################
#                             Overloaded Operators                            #

    def __init__(self, app, uuid: str, **kwargs):
        """
        Initialize Button Element..

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
        """
        Calcualte the stare of the button and which color to display.

        Returns
        -------
        None.

        """
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


    @abstractmethod  # noqa
    def _containing(self, pos_x: int, pos_y: int) -> bool:
        """
        Calculate if the mouse cursor is contained in the shape.

        Parameters
        ----------
        pos_x : integer
            Coordinate x of the mouse.
        pos_y : integer
            Coordinate y of the mouse.

        Raises
        ------
        NotImplementedError
            Method not implemented, child class must implement it.

        Returns
        -------
        bool
            DESCRIPTION.

        """
        raise NotImplementedError(
            "Method not implemented, child class must implement it."
        )

    def _render(self):
        """
        Execute exlusively the render process.

        Returns
        -------
        None.

        """
        # Render button (draw quad as two triangles)
        self.__vao.render(mgl.TRIANGLE_STRIP)

        # Render possible text on button
        self.__text.render()

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
            "x": 0,
            "y": 0,
            "default_color": (1.0, 1.0, 1.0),
            "hover_color": None,
            "locked_color": None,
            "text": None,
        }

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        if self.app.DEBUG:
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
            self.uuid + "_text",
            **kwargs['text'],
        )

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

        if self.app.DEBUG:
            print("Shader program compiled and linked successfully.")

    def _set_vao(self):
        """
        Set the vertex array object.

        Returns
        -------
        None.

        """
        self._set_vbo()

        self.__vao = self.app.ctx.vertex_array(
            self.__shader_programs, [(self.__vbo, '3f', 'in_vert')])

    def _set_vbo(self):
        """
        Set the vertex buffer object.

        Returns
        -------
        None.

        """
        self._set_vertexes()

        self.__vbo = self.app.ctx.buffer(self.vertexes.tobytes())

    @abstractmethod
    def _set_vertexes(self):
        raise NotImplementedError

###############################################################################


###############################################################################
#                                Public Methods                               #

    def check_click(self, mouse_position: tuple[int, int]) -> str | None:  # noqa
        """
        Check if a click has been on the button,

        Parameters
        ----------
        mouse_position : Tuple[integer, integer]
            Position of the mouse, tuple of integers (pixels) x, y.

        Returns
        -------
        string or None
            UUID of the Element if clicked or None if not.

        """
        # Cannot be clicked if is locked
        if self.is_locked or self.is_hidden:
            return None

        # Get mouse coordinates
        mx, my = mouse_position

        # Return UUID if button is clicked
        if self._containing(mx, my):
            return self.uuid

        return None

    def check_hover(self, mouse_position: tuple[int, int]):
        """
        Check if the mouse is hovering on top of the button.

        Parameters
        ----------
        mouse_position : Tuple[integer, integer]
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

    def check_motion(self, mouse_position: tuple[int, int]) -> str | None:
        """
        Check if when moving the mouse is inside the button when moved.

        Parameters
        ----------
        mouse_position : tuple[integer, integer]
            Mouse position in x and y coordinates of the window.

        Raises
        ------
        NotImplementedError
            Method not implemented, child class must implement it.

        Returns
        -------
        string or None
            UUID of the Element if moved on or None if not.

        """
        # Cannot be moved on if is locked
        if self.is_locked or self.is_hidden:
            return None

        # Get mouse coordinates
        mx, my = mouse_position

        # Return UUID if button is unclicked
        if self._containing(mx, my):
            return self.uuid

        return None

    def check_unclick(self, mouse_position: tuple[int, int]) -> str | None:
        """
        Check if it has been unclicked on the Element.

        Parameters
        ----------
        mouse_position : tuple[integer, integer]
            Mouse position in x and y coordinates of the window.

        Returns
        -------
        None.
            UUID of the Element if unclicked or None if not.

        """
        # Cannot be unclicked if is locked
        if self.is_locked or self.is_hidden:
            return None

        # Get mouse coordinates
        mx, my = mouse_position

        # Return UUID if button is unclicked
        if self._containing(mx, my):
            return self.uuid

        return None

    def destroy(self):
        """
        Destroy all OpenGL object and release memory.

        Returns
        -------
        None.

        """
        self.__vbo.release()

        self.__vao.release()

        self.__shader_programs.release()

    def render(self):
        """
        Render logic.

        Returns
        -------
        None.

        """
        if self.is_hidden:
            return None

        self.__calculate_state()

        self._render()

    def toggle(self):
        """
        Button has no toggle position, return None always.

        Returns
        -------
        None.

        """
        return None

    def untoggle(self):
        """
        Button has no toggle position, return None always.

        Returns
        -------
        None.

        """
        return None

###############################################################################


###############################################################################
#                                  Properties                                 #

    @property  # noqa
    def color(self) -> tuple[float, float, float]:
        """
        Get OpenGL color from the shader.

        Returns
        -------
        tuple[float, float, float]
            Tuple describing the RGB color as floats from 0 to 1.

        """
        return self.__shader_programs['in_colour'].value

    @color.setter
    def color(self, new_color: tuple[float, float, float]):
        """
        Set OpenGL color from the shader.

        Parameters
        ----------
        new_color : tuple[float, float, float]
            Tuple describing the RGB color as floats from 0 to 1.

        Returns
        -------
        None.

        """
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
    def locked_color(self) -> tuple[float, float, float]:
        return self.__locked_color

    @locked_color.setter
    def locked_color(self, new_locked_color: tuple[float, float, float]):
        self.__locked_color = new_locked_color

    @property
    def is_hovered(self):
        return self.__is_hovered

    @property
    def text(self) -> TextLabel:
        return self.__text

    @property
    @abstractmethod
    def vertexes(self):
        raise NotImplementedError

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
