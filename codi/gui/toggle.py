# -*- coding: utf-8 -*- noqa
"""
Created on Wed Dec 11 22:39:09 2024

@author: Joel Tapia Salvador
"""
from .rectangular_button import RectangularButton
""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


class Toggle():

    __slots__ = (
        "__app",
        "__is_toggled",
        "__toggle_color",
        "__uuid",
    )

###############################################################################
#                             Overloaded Operators                            #

    def __init__(self, app, uuid: str, **kwargs):
        raise NotImplementedError


###############################################################################


###############################################################################
#                               Private Methods                               #

def _set_attributes(self, app, uuid: str, **kwargs):
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
        print("Toggle")
        print(kwargs)

    # Color information
    self.__toggle_color = kwargs["toggle_color"]

    # States information
    self.__is_toggled = kwargs["toggle"]

###############################################################################


###############################################################################
#                              Protected Methods                              #

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

###############################################################################


###############################################################################
#                                Public Methods                               #

    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        clicked = super().check_click(mouse_pos)

        if clicked:
            self.__is_toggled = not self.__is_toggled

        return clicked

    def render(self):
        if self.is_hidden:
            return None

        if self.__app.DEBUG:
            print(f'Toggled: {self.is_toggled}')

        self.__calculate_state()

        super()._render()


###############################################################################


###############################################################################
#                                  Properties                                 #


    @property
    def is_toggled(self):
        return self.__is_toggled

    @property
    def toggle_color(self) -> tuple[float, float, float]:
        return self.__toggle_color

    @toggle_color.setter
    def toggle_color(self, new_toggle_color: tuple[float, float, float]):
        self.toggle_color = new_toggle_color

###############################################################################
