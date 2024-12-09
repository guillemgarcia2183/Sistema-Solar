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
        "__app",
        "__is_hidden",
        "__is_hovered",
        "__is_locked",
        "__uuid",
    )

    def __init__(self, app=None, uuid: str = None, **kwargs):
        self.__app = None

        self.__uuid = None

        self.__is_hidden = None
        self.__is_hovered = None
        self.__is_locked = None

    def check_click(self, mouse_position: tuple[int, int]):
        """
        Empty check_click method.

        Parameters
        ----------
        mouse_position : tuple[int, int]
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
        mouse_position : tuple[int, int]
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

    def render(self):
        """
        Empty render method.

        Returns
        -------
        None.

        """
        return None
