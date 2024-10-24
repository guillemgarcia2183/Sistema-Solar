# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 02:37:14 2024

@author: Joel Tapia Salvador
"""
from .circular_button import CircularButton
from .rectangular_button import RectangularButton

from typing import Tuple, Dict


class ButtonManager():
    __slots__ = ("__app", "__buttons_buffer", "__types_buttons")

    def __init__(self, app):
        self.__app = app

        self.__buttons_buffer = {}

        self.__types_buttons = {
            "circular": CircularButton,
            "rectangular": RectangularButton,
        }

    def __add_button(self, new_button):
        try:
            self.__buttons_buffer[new_button.uuid]

            raise ValueError(f'A button with uuid: {new_button.uuid} already exists.')

        except KeyError:
            self.__buttons_buffer[new_button.uuid] = new_button

    def add_button(
            self,
            button_type: str,
            uuid: str,
            params: Dict[str, object]
    ):
        try:
            self.__types_buttons[button_type]
        except KeyError as error:
            raise ValueError(f'Type of button: {button_type} does not exist.') from error

        new_button = self.__types_buttons[button_type](
            self.__app,
            uuid,
            **params
        )

        self.__add_button(new_button)

    def add_circular_button(
            self,
            uuid: str,
            x: int,
            y: int,
            radius: int,
            default_color: Tuple[float, float, float],
            hover_color: Tuple[float, float, float] | None = None,
            locked_color: Tuple[float, float, float] | None = None,
            hidden: bool = False,
            locked: bool = False,

    ):
        params = {
            "x": x,
            "y": y,
            "radius": radius,
            "default_color": default_color,
            "hover_color": hover_color,
            "locked_color": locked_color,
            "hidden": hidden,
            "locked": locked,

        }

        self.add_button('circular', uuid, params)

    def add_rectangular_button(
        self,
        uuid: str,
        x: int,
        y: int,
        width: int,
        height: int,
        default_color: Tuple[float, float, float],
        hover_color: Tuple[float, float, float] | None = None,
        locked_color: Tuple[float, float, float] | None = None,
        hidden: bool = False,
        locked: bool = False,
    ):

        params = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "default_color": default_color,
            "hover_color": hover_color,
            "locked_color": locked_color,
            "hidden": hidden,
            "locked": locked,
        }

        self.add_button('rectangular', uuid, params)

    def batch_add_buttons(self, batch: Dict[str, Dict[str, object]]):
        for uuid, meta in batch.items():
            self.add_button(meta['class'], uuid, meta['kwargs'])

    def check_click(self, mouse_position: Tuple[int, int]) -> str | None:
        for button in self.__buttons_buffer.values():
            if button.check_click(mouse_position):
                return button.uuid
        return None

    def check_hover(self, mouse_position: Tuple[int, int]) -> None:
        for button in self.__buttons_buffer.values():
            button.check_hover(mouse_position)

    def destroy(self) -> None:
        for button in list(self.__buttons_buffer.values()):
            button.destroy()
            del self.__buttons_buffer[button.uuid]

    def remove(self, uuid: str) -> None:
        try:
            self.__buttons_buffer[uuid]
        except KeyError as error:
            raise ValueError(f'Button with uuid: {uuid} does not exist.') from error

        self.__buttons_buffer[uuid].destroy()
        del self.__buttons_buffer[uuid]

    def render(self) -> None:
        for button in self.__buttons_buffer.values():
            button.render()
