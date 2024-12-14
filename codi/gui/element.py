# -*- coding: utf-8 -*- noqa
"""
Created on Mon Dec  9 02:43:03 2024

@author: Joel Tapia Salvador
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package module file.' +
        ' Execute a main instead and import the module.')


from abc import ABC, abstractmethod


class Element(ABC):
    """Empty class."""

    __slots__ = (
        "__app",
        "__is_hidden",
        "__is_locked",
        "__uuid",
    )

###############################################################################
#                             Overloaded Operators                            #

    def __init__(self, app, uuid: str, **kwargs):
        # Engine
        self.__app = app

        # Element UUID
        self.__uuid = uuid

        default_kwargs = {
            "hidden": False,
            "locked": False,
        }

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        # States information
        self.__is_hidden = kwargs["hidden"]
        self.__is_locked = kwargs["locked"]


###############################################################################


###############################################################################
#                                Public Methods                               #

    @abstractmethod  # noqa
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

    @abstractmethod
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

    @abstractmethod
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

    def hide(self):
        """
        Hide Element.

        Returns
        -------
        None.

        """
        self.__is_hidden = True

    def lock(self):
        """
        Lock Element.

        Returns
        -------
        None.

        """
        self.__is_locked = True

    @abstractmethod
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

    @abstractmethod
    def toggle(self):
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

    def unhide(self):
        """
        Un-hide element.

        Returns
        -------
        None.

        """
        self.__is_hidden = False

    def unlock(self):
        """
        Un-lock Element.

        Returns
        -------
        None.

        """
        self.__is_locked = False

    @abstractmethod
    def untoggle(self):
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

###############################################################################


###############################################################################
#                                  Properties                                 #

    @property  # noqa
    def app(self):
        """
        Return app engine.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self.__app

    @property
    def is_hidden(self) -> bool:
        """
        Return if Element is hidden.

        Returns
        -------
        bool
            Is hidden.

        """
        return self.__is_hidden

    @property
    @abstractmethod
    def is_hovered(self) -> bool:
        """
        Template Element.

        Return if Element is hovered.

        Raises
        ------
        NotImplementedError
            Method not implemented.

        Returns
        -------
        bool
            Is hovered.

        """
        raise NotImplementedError

    @property
    def is_locked(self) -> bool:
        """
        Return if Element is locked.

        Returns
        -------
        bool
            Is locked.

        """
        return self.__is_locked

    @property
    def uuid(self) -> str:
        """
        Return Element UUID.

        Returns
        -------
        str
            Element UUID.

        """
        return self.__uuid

###############################################################################
