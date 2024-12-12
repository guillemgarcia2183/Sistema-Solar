# -*- coding: utf-8 -*- noqa
"""
Created on Wed Oct 23 02:37:14 2024

@author: Joel Tapia Salvador
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


from .circular_button import CircularButton
from .circular_toggle import CircularToggle
from .element import Element
from .rectangular_button import RectangularButton
from .rectangular_toggle import RectangularToggle
from .text import Text


class GUIManager():

    __slots__ = (
        "__app",
        "__elements_buffer",
        "__types_elements"
    )

    def __init__(self, app):
        self.__app = app

        self.__elements_buffer: dict[str, Element] = {}

        self.__types_elements: dict[str, Element] = {
            "circular_button": CircularButton,
            "circular_toggle": CircularToggle,
            "rectangular_button": RectangularButton,
            "rectangular_toggle": RectangularToggle,
            "text": Text,
        }

    def __add_element(self, new_element: Element):
        """
        Add an Element object with an uuid to the buttons buffer.

        Parameters
        ----------
        new_element : Element
            DESCRIPTION.

        Raises
        ------
        ValueError
            An Element with given uuid alredy exists.

        Returns
        -------
        None.

        """
        if not issubclass(type(new_element), Element):
            raise TypeError("Not a subclass of Element.")

        try:
            self.__elements_buffer[new_element.uuid]

            raise ValueError(f'An Element with uuid: {new_element.uuid} already exists.')

        except KeyError:
            self.__elements_buffer[new_element.uuid] = new_element

    def add_element(
        self,
        element_type: str,
        uuid: str,
        params: dict[str, object]
    ):
        """
        Add an Element of a given type with a given uuid and the parametres.

        Parameters
        ----------
        element_type : str
            DESCRIPTION.
        uuid : str
            DESCRIPTION.
        params : Dict[str, object]
            DESCRIPTION.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if self.__app.DEBUG:
            print(f'Adding: {element_type}')
        try:
            self.__types_elements[element_type]
        except KeyError as error:
            raise ValueError(f'Type of Element: {element_type} does not exist.') from error

        new_element = self.__types_elements[element_type](
            self.__app,
            uuid,
            **params
        )

        self.__add_element(new_element)

    def add_circular_button(
        self,
        uuid: str,
        x: int,
        y: int,
        radius: int,
        default_color: tuple[float, float, float],
        hover_color: tuple[float, float, float] | None = None,
        locked_color: tuple[float, float, float] | None = None,
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

        self.add_element('circular_button', uuid, params)

    def add_rectangular_button(
        self,
        uuid: str,
        x: int,
        y: int,
        width: int,
        height: int,
        default_color: tuple[float, float, float],
        hover_color: tuple[float, float, float] | None = None,
        locked_color: tuple[float, float, float] | None = None,
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

        self.add_element('rectangular_button', uuid, params)

    def batch_add_elements(self, batch: dict[str, dict[str, object]]):
        for uuid, meta in batch.items():
            for element in meta['kwargs'].keys():
                if element == 'x':
                    meta['kwargs'][element] *= self.__app.WIN_SIZE[0]
                elif element == 'y':
                    meta['kwargs'][element] *= self.__app.WIN_SIZE[1]
                elif element in ('radius', 'height', 'width', 'x', 'y'):
                    meta['kwargs'][element] *= min(self.__app.WIN_SIZE)

            self.add_element(meta['class'], uuid, meta['kwargs'])

    def check_click(self, mouse_position: tuple[int, int]) -> str | None:
        for element in self.__elements_buffer.values():
            if element.check_click(mouse_position):
                return element.uuid
        return None

    def check_hover(self, mouse_position: tuple[int, int]) -> None:
        for element in self.__elements_buffer.values():
            element.check_hover(mouse_position)

    def destroy(self) -> None:
        for element in list(self.__elements_buffer.values()):
            element.destroy()
            del self.__elements_buffer[element.uuid]

    def remove(self, uuid: str) -> None:
        try:
            self.__elements_buffer[uuid]
        except KeyError as error:
            raise ValueError(f'Element with uuid: {uuid} ' + ' does not exist.') from error

        self.__elements_buffer[uuid].destroy()
        del self.__elements_buffer[uuid]

    def render(self) -> None:
        for element in self.__elements_buffer.values():
            element.render()
