# -*- coding: utf-8 -*- noqa
"""
Created on Mon Dec  9 02:43:03 2024

@author: Joel Tapia Salvador
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package module file.' +
        ' Execute a main instead and import the module.')


class Element():
    """Empty class."""

    __slots__ = (
        "__app",
        "__is_hidden",
        "__is_hovered",
        "__is_locked",
        "__uuid",
    )

    def __init__(self, app, uuid: str, **kwargs):
        raise NotImplementedError

    def check_click(self, mouse_position: tuple[int, int]):
        """
        Template Element.

        Parameters
        ----------
        mouse_position : tuple[int, int]
            DESCRIPTION.

        Raises
        ------
        NotImplementedError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        raise NotImplementedError

    def check_hover(self, mouse_position: tuple[int, int]):
        """
        Template Element.

        Parameters
        ----------
        mouse_position : tuple[int, int]
            DESCRIPTION.

        Raises
        ------
        NotImplementedError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        raise NotImplementedError

    def destroy(self):
        """
        Template Element.

        Raises
        ------
        NotImplementedError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        raise NotImplementedError

    def render(self):
        """
        Template Element.

        Raises
        ------
        NotImplementedError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        raise NotImplementedError
