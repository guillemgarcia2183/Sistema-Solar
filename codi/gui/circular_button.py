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
import moderngl as mgl

from math import acos, ceil, cos, pi, sin

from .button import Button


class CircularButton(Button):

    __slots__ = (
        "__radius",
        "__vertexes",
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

    def _containing(self, pos_x, pos_y) -> bool:  # noqa
        return (
            (pos_x - self.x) ** 2 + (pos_y - self.y) ** 2
        ) <= self.radius ** 2

    def _set_attributes(self, app, uuid: str, **kwargs):
        default_kwargs = {
            "radius": 1,
        }

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        if self.app.DEBUG:
            print(kwargs)

        # Shape information
        self.__radius = kwargs["radius"]

    def _set_vertexes(self):
        # Vertex data (circle for the button)

        error = 0.5

        tolerance = acos(2 * (1 - error / self.radius) ** 2 - 1)

        number_circumference_vertexes = ceil(2 * pi / tolerance)

        angle = 2 * pi / number_circumference_vertexes

        origin_vertex = [2 * (
            (self.x - (self.app.WIN_SIZE[0] / 2)
             ) / (
                self.app.WIN_SIZE[0]
            )), - 2 * ((
                self.y - (self.app.WIN_SIZE[1] / 2)
            ) / (
                self.app.WIN_SIZE[1]
            )), 0.0]

        circumference_vertexes = [
            [2 * (
                (self.x + self.radius *
                 cos(angle * i) - (self.app.WIN_SIZE[0] / 2)
                 ) / (
                    self.app.WIN_SIZE[0]
                )), - 2 * ((
                    self.y + self.radius *
                    sin(angle * i) - (self.app.WIN_SIZE[1] / 2)
                ) / (
                    self.app.WIN_SIZE[1]
                )), 0.0
             ] for i in range(number_circumference_vertexes)]

        gl = [
            [
                origin_vertex,
                circumference_vertexes[i % number_circumference_vertexes],
                circumference_vertexes[(i + 1) % number_circumference_vertexes]
            ] for i in range(number_circumference_vertexes)
        ]

        self.__vertexes = np.array(
            gl,
            dtype='f4'
        ).flatten('C')

###############################################################################


###############################################################################
#                                  Properties                                 #


    @property  # noqa
    def radius(self) -> int:
        return self.__radius

    @radius.setter
    def radius(self, new_radius: int):
        self.__radius = new_radius

        self._set_vao()

    @property
    def vertexes(self):
        return self.__vertexes

###############################################################################
