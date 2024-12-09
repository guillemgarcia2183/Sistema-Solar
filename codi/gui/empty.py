# -*- coding: utf-8 -*- noqa
"""
Created on Thu Nov 28 04:03:13 2024

@author: JoelT
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package module file.' +
        ' Execute a main instead and import the module.')


class Empty():
    """Empty class."""

    def __init__(self):
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
