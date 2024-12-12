# -*- coding: utf-8 -*- noqa
"""
Created on Thu Oct 17 12:06:14 2024

@author: Joel Tapia Salvador
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


import numpy as np

from .button import Button


class RectangularButton(Button):

    __slots__ = (
        "__app",
        "__height",
        "__uuid",
        "__vertexes",
        "__width",
    )

###############################################################################
#                             Overloaded Operators                            #

    def __init__(self, app, uuid: str, **kwargs):
        # Inicialize attributes
        super()._set_attributes(app, uuid, **kwargs)
        self._set_attributes(app, uuid, **kwargs)

        # Write the shader
        super()._set_shader_programs()

        # Create all ModernGL objects
        super()._set_vao()

###############################################################################


###############################################################################
#                               Private Methods                               #

    def _containing(self, pos_x, pos_y):
        return (
            self.x - self.width / 2 <= pos_x <= self.x + self.width / 2
        ) and (
            self.y - self.height / 2 <= pos_y <= self.y + self.height / 2
        )

    def _set_attributes(self, app, uuid, **kwargs):
        default_kwargs = {
            "width": 1,
            "height": 1,
        }

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        # Engine
        self.__app = app

        # Button's unique id
        self.__uuid = uuid

        if self.__app.DEBUG:
            print("Rectangular Button")
            print(kwargs)

        # Shape information
        self.__width = kwargs["width"]
        self.__height = kwargs["height"]

    def _set_vertexes(self):

        # Vertex data (rectangle for the button)
        gl_x = (
            2 * (
                (
                    self.x - (self.width / 2) -
                    (self.__app.WIN_SIZE[0] / 2)
                ) / (
                    self.__app.WIN_SIZE[0]
                )
            ),
            2 * (
                (
                    self.x + (self.width / 2) -
                    (self.__app.WIN_SIZE[0] / 2)
                ) / (
                    self.__app.WIN_SIZE[0]
                )
            )
        )

        gl_y = (
            -2 * (
                (
                    self.y - (self.height / 2) -
                    (self.__app.WIN_SIZE[1] / 2)
                ) / (
                    self.__app.WIN_SIZE[1]
                )
            ),
            -2 * (
                (
                    self.y + (self.height / 2) -
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

###############################################################################


###############################################################################
#                                  Properties                                 #

    @property
    def height(self) -> int:
        return self.__height

    @height.setter
    def height(self, new_height: int):
        self.__height = new_height

        self.__set_vao()

    @property
    def width(self) -> int:
        return self.__width

    @width.setter
    def width(self, new_width: int):
        self.__width = new_width

        self.__set_vao()

    @property
    def vertexes(self):
        return self.__vertexes

###############################################################################
