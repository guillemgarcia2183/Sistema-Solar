# -*- coding: utf-8 -*- noqa
"""
Created on Wed Dec 11 22:19:55 2024

@author: Joel Tapia Salvador
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


import moderngl
import numpy as np
import pygame as pg

from .circular_button import CircularButton


class CircularToggle(CircularButton):

    __slots__ = (
        "__app",
        "__default_color",
        "__height",
        "__hover_color",
        "__is_hidden",
        "__is_hovered",
        "__is_locked",
        "__is_toggled",
        "__locked_color",
        "__shader_programs",
        "__text",
        "__toggle_color",
        "__uuid",
        "__vao",
        "__vbo",
        "__vertexes",
        "__width",
        "__x",
        "__y",
    )

    def __init__(self, app, uuid: str, **kwargs):

        super().__init__(app, uuid, **kwargs)

        default_kwargs = {
            "toggle_color": (0.0, 0.0, 0.0),
            "toggle": False,
        }

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        # Engine
        self.__app = app

        # Button's unique id
        self.__uuid = uuid

        if self.__app.DEBUG:
            print(kwargs)

        # Color information
        self.__toggle_color = kwargs["toggle_color"]

        # States information
        self.__is_toggled = kwargs["toggle"]

    def __calculate_state(self):
        # Set color based on state
        if self.is_locked:
            self.color = self.locked_color
        elif self.is_hovered:
            self.color = self.hover_color
        elif self.is_toggled:
            self.color = self.toggle_color
        else:
            self.color = self.default_color

    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        clicked = super().check_click(mouse_pos)

        if clicked:
            self.__is_toggled = not self.__is_toggled

        return clicked

    @property
    def is_toggled(self):
        return self.__is_toggled

    @property
    def toggle_color(self) -> tuple[float, float, float]:
        return self.__toggle_color

    @toggle_color.setter
    def toggle_color(self, new_toggle_color: tuple[float, float, float]):
        self.toggle_color = new_toggle_color

    def render(self):
        if self.is_hidden:
            return None

        if self.__app.DEBUG:
            print(f'Toggled: {self.is_toggled}')

        self.__calculate_state()

        super()._render()