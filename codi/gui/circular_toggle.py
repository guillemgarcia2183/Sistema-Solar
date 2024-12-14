# -*- coding: utf-8 -*- noqa
"""
Created on Wed Dec 11 22:19:55 2024

@author: Joel Tapia Salvador
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


from .circular_button import CircularButton


class CircularToggle(CircularButton):

    __slots__ = (
        "__is_toggled",
        "__toggle_color",
    )

###############################################################################
#                             Overloaded Operators                            #

    def __init__(self, app, uuid: str, **kwargs):

        super().__init__(app, uuid, **kwargs)

        default_kwargs = {
            "toggle_color": (0.0, 0.0, 0.0),
            "toggle": False,
        }

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        if self.app.DEBUG:
            print(kwargs)

        # Color information
        self.__toggle_color = kwargs["toggle_color"]

        # States information
        self.__is_toggled = kwargs["toggle"]

###############################################################################


###############################################################################
#                               Private Methods                               #


    def __calculate_state(self):  # noqa
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
        click = super().check_click(mouse_pos)

        if click:
            if self.is_toggled:
                self.untoggle()
            else:
                self.toggle()

        return click

    def render(self):
        if self.is_hidden:
            return None

        # if self.app.DEBUG:
        #     print(f'Toggled: {self.is_toggled}')

        self.__calculate_state()

        super()._render()

    def toggle(self):
        self.__is_toggled = True

    def untoggle(self):
        self.__is_toggled = False

###############################################################################


###############################################################################
#                                  Properties                                 #

    @property  # noqa
    def is_toggled(self):
        return self.__is_toggled

    @property
    def toggle_color(self) -> tuple[float, float, float]:
        return self.__toggle_color

    @toggle_color.setter
    def toggle_color(self, new_toggle_color: tuple[float, float, float]):
        self.toggle_color = new_toggle_color

###############################################################################
