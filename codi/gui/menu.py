# -*- coding: utf-8 -*- noqa

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


from typing import Any, Optional

from .gui_manager import GUIManager
from .circular_toggle import CircularToggle
from .rectangular_toggle import RectangularToggle

TOGGLE_BUTTONS = {
    "circular_toggle": CircularToggle,
    "rectangular_toggle": RectangularToggle
}


class Menu(GUIManager):
    """Menu Element."""

    __slots__ = (
        "__is_visible",
        "__menu_button",
        "__uuid",
    )

###############################################################################
#                             Overloaded Operators                            #

    def __init__(self, app, uuid: str, **kwargs: Optional[dict[str, Any]]):
        """
        Initialize a menu with toggle and additional buttons.

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
        super().__init__(app)

        self._set_attributes(app, uuid, **kwargs)


###############################################################################


###############################################################################
#                               Private Methods                               #


    def _set_attributes(self, app, uuid, **kwargs: Optional[dict[str, Any]]):  # noqa
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
        default_kwargs = {
            "toggle_button": {
                "class": "rectangular_toggle",
                "kwargs": {
                    "x": 0,
                    "y": 0,
                    "width": 10,
                    "height": 5,
                    "default_color": [
                        1.0,
                        1.0,
                        1.0
                    ],
                    "hover_color": [
                        0.5,
                        0.5,
                        0.5
                    ],
                    "toggle_color": [
                        1.0,
                        1.0,
                        0.0
                    ],
                    "locked_color": [
                        0.5,
                        0.5,
                        0.5
                    ],
                    "text": {
                        "text": "Menu",
                        "color": [
                            0.0,
                            0.0,
                            0.0
                        ],
                        "sys_font": "Arial",
                        "font_size": 12,
                        "scale_factor": 2
                    }
                }
            },
            "hidden": False,
            "locked": False,
            "elements": {

            },
        }

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        if self.app.DEBUG:
            print("Menu")
            print(kwargs)

        self.__uuid = uuid

        self.__menu_button = TOGGLE_BUTTONS[kwargs["toggle_button"]["class"]](
            self.app,
            self.uuid + "toggle_button",
            **kwargs["toggle_button"]["kwargs"],
        )

        if kwargs["hidden"]:
            self.__menu_button.hide()
        else:
            self.__menu_button.unhide()

        if kwargs["locked"]:
            self.__menu_button.lock()
        else:
            self.__menu_button.unlock()

        self.__is_visible = False

        super().batch_add_elements(kwargs["elements"], False)
        super().hide()

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
        if self.is_locked or self.is_hidden:
            return None

        if self.__menu_button.check_click(mouse_position):
            if self.is_visible:
                self.unvisualize()
            else:
                self.visualize()

        if self.is_visible:
            click = super().check_click(mouse_position)
            if click:
                self.unvisualize()
                self.__menu_button.untoggle()
            return click
        else:
            return self.uuid

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
        if self.is_locked or self.is_hidden:
            return None

        self.__menu_button.check_hover(mouse_position)

        if self.is_visible:
            super().check_hover(mouse_position)

    def destroy(self):
        """
        Destroy all OpenGL object and release memory.

        Returns
        -------
        None.

        """
        self.__menu_button.destroy()

        super().destroy()

    def hide(self):
        """
        Hide full menu, including menu button.

        Returns
        -------
        None.

        """
        self.__menu_button.hide()

        self.unvisualize()

    def lock(self):
        """
        Lock menu, hidding elements from menu and locking them too.

        Returns
        -------
        None.

        """
        self.__menu_button.lock()

        self.unvisualize()

        super().lock()

    def render(self):
        """
        Render logic.

        Returns
        -------
        None.

        """
        if self.is_hidden:
            return None

        self.__menu_button.render()

        super().render()

    def unhide(self):
        """
        Unhide menu button.

        Returns
        -------
        None.

        """
        self.__menu_button.unhide()

    def unlock(self):
        """
        Unlock menu button and menu Elements.

        Returns
        -------
        None.

        """
        self.__menu_button.unlock()

        super().unlock()

    def unvisualize(self):
        """
        Hide all menu Elements.

        Returns
        -------
        None.

        """
        self.__is_visible = False

        super().hide()

    def visualize(self):
        """
        Show all menu Elements.

        Returns
        -------
        None.

        """
        if self.is_hidden or self.is_locked:
            return None

        self.__is_visible = True

        super().unhide()

###############################################################################


###############################################################################
#                                  Properties                                 #

    @property  # noqa
    def is_hidden(self) -> bool:
        """
        Say if the menu is hidden.

        Returns
        -------
        bool
            If the menu is hidden.

        """
        return self.__menu_button.is_hidden

    @property
    def is_hovered(self) -> bool:
        """
        Say if the mouse is hovering above the menu button.

        Returns
        -------
        bool
            If the mouth is hovering above.

        """
        return self.__menu_button.is_hovered

    @property
    def is_locked(self) -> bool:
        """
        Say if the menu is locked.

        Returns
        -------
        bool
            DESCRIPTION.

        """
        return self.__menu_button.is_locked

    @property
    def is_visible(self) -> bool:
        """
        Say if the menu Elemeents are visible.

        Returns
        -------
        bool
            DESCRIPTION.

        """
        return self.__is_visible

    @property
    def uuid(self) -> str:
        """
        Say Menu uuid.

        Returns
        -------
        str
            DESCRIPTION.

        """
        return self.__uuid

###############################################################################
