# -*- coding: utf-8 -*- noqa
"""
Created on Thu Nov 28 04:03:13 2024

@author: JoelT
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package module file.' +
        ' Execute a main instead and import the module.')


from .element import Element


class Empty(Element):
    """Empty class."""

    __slots__ = (
        "__is_hovered",
    )

###############################################################################
#                             Overloaded Operators                            #

    def __init__(self, app=None, uuid: str = None, **kwargs):
        super().__init__(app, uuid, **kwargs)

        self.__is_hovered = None

###############################################################################


###############################################################################
#                                Public Methods                               #


    def check_click(self, mouse_position: tuple[int, int]):  # noqa
        """
        Empty check_click method.

        Parameters
        ----------
        mouse_position : tuple[integer, integer]
            DESCRIPTION.

        Returns
        -------
        None.

        """
        return None

    def check_hover(self, mouse_position: tuple[int, int]):
        """
        Empty check_hover method.

        Parameters
        ----------
        mouse_position : tuple[integer, integer]
            DESCRIPTION.

        Returns
        -------
        None.

        """
        return None

    def check_unclick(self, mouse_position: tuple[int, int]):  # noqa
        """
        Empty check_unclick method.

        Parameters
        ----------
        mouse_position : tuple[integer, integer]
            DESCRIPTION.

        Returns
        -------
        None.

        """
        return None

    def destroy(self):
        """
        Empty destroy method.

        Returns
        -------
        None.

        """
        return None

    def hide(self):
        """
        Emty hide method.

        Returns
        -------
        None.

        """
        self.__is_hidden = None

    def lock(self):
        """
        Empty lock method.

        Returns
        -------
        None.

        """
        self.__is_locked = None

    def render(self):
        """
        Empty render method.

        Returns
        -------
        None.

        """
        return None

    def toggle(self):
        """
        Empty toggle method.

        Returns
        -------
        None.

        """
        return None

    def unhide(self):
        """
        Empty unhide method.

        Returns
        -------
        None.

        """
        self.__is_hidden = None

    def unlock(self):
        """
        Empty unlock method.

        Returns
        -------
        None.

        """
        self.__is_locked = None

    def untoggle(self):
        """
        Empty untoggle method.

        Returns
        -------
        None.

        """
        return None

###############################################################################


###############################################################################
#                                  Properties                                 #

    @property  # noqa
    def is_hovered(self):
        """
        Empty is_hovered property.

        Returns
        -------
        None.

        """
        return self.__is_hovered
###############################################################################
