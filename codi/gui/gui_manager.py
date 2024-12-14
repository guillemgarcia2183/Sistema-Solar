# -*- coding: utf-8 -*- noqa
"""
Created on Wed Oct 23 02:37:14 2024

@author: Joel Tapia Salvador
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


from typing import Any

from .element import Element


class GUIManager(Element):

    __slots__ = (
        "__app",
        "__elements_buffer",
        "__types_elements",
    )

###############################################################################
#                             Overloaded Operators                            #

    def __init__(self, app):
        self.__app = app

        self.__elements_buffer: dict[str, type[Element]] = {}

        # !!! This imports are put here to avoid Circular ImportError !!!
        # !!! DON'T MOVE !!!
        from .circular_button import CircularButton
        from .circular_toggle import CircularToggle
        from .menu import Menu
        from .rectangular_button import RectangularButton
        from .rectangular_toggle import RectangularToggle
        # from .slider import Slider
        from .text import Text

        self.__types_elements: dict[str, type[Element]] = {
            "circular_button": CircularButton,
            "circular_toggle": CircularToggle,
            "menu": Menu,
            "rectangular_button": RectangularButton,
            "rectangular_toggle": RectangularToggle,
            # "slider": Slider,
            "text": Text,
        }

    def __getitem__(self, uuid: str) -> type[Element]:
        """
        Get GUI Element with the uuid of it.

        Get GUI Element with the uuid of it. Can use to alterate properties of 
        the Element.
        Do *NOT* use to remove or destroy a uuid element, it will create
        bugs and errors, use thee "remove" method of the GUIManager for that.

        Parameters
        ----------
        uuid : string
            UUID of the Element to get.

        Raises
        ------
        KeyError
            The provided UUID has not been found in the GUI.

        Returns
        -------
        type[Element]
            Subclass of Element.

        """
        try:
            return self.__elements_buffer[uuid]
        except KeyError as error:
            raise KeyError(f'Element with uuid: "{uuid}" '
                           + 'does not exist.') from error

###############################################################################


###############################################################################
#                              Protected Methods                              #


    def __add_element(self, new_element: type[Element]):  # noqa
        """
        Add an Element object with an uuid to the elements buffer.

        Parameters
        ----------
        new_element : type[Element]
            Subclass of Element.

        Raises
        ------
        TypeError
            The element given is not a subclass of Element.
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

            raise ValueError(f'An Element with uuid: "{new_element.uuid}" already exists.')

        except KeyError:
            self.__elements_buffer[new_element.uuid] = new_element

###############################################################################


###############################################################################
#                               Private Methods                               #


    def _autosize(  # noqa
        self,
        element_property_name: str,
        element_property_value: Any,
    ) -> Any:
        """
        Autosize elements size and positions to window dimensions.

        If the property is "x", "y", "radius", "height" or "width" autosizes it
        to the dimension of the window, if not, returns them exactly like they
        are.

        Parameters
        ----------
        element_property_name : string
            String representing the name of the property.
        element_property_value : Any
            Property.

        Returns
        -------
        Any
            Property.

        """
        if element_property_name == 'x':
            element_property_value *= self.app.WIN_SIZE[0]
        elif element_property_name == 'y':
            element_property_value *= self.app.WIN_SIZE[1]
        elif element_property_name in ('radius', 'height', 'width', 'x', 'y'):
            element_property_value *= min(self.app.WIN_SIZE)

        return element_property_value

    def _parse_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Parse a dictionary of keywords arguments.

        Parse a dictionary of keywords arguments that can include more
        dictionaries of keywords arguments.

        Parameters
        ----------
        kwargs : dict[string, Any]
            Dictionary of pair keyword (string) to any type.

        Returns
        -------
        dict[string, Any]
            Dictionary of pair keyword (string) to any type.

        """
        for element_property_name in kwargs.keys():
            if isinstance(kwargs[element_property_name], dict):
                kwargs[element_property_name] = self._parse_kwargs(
                    kwargs[element_property_name]
                )
            else:
                kwargs[element_property_name] = self._autosize(
                    element_property_name, kwargs[element_property_name])
        return kwargs


###############################################################################


###############################################################################
#                                Public Methods                               #


    def add_element(  # noqa
        self,
        element_type: str,
        uuid: str,
        params: dict[str, Any]
    ):
        """
        Add an Element of a given type with a given uuid and the parametres.

        Parameters
        ----------
        element_type : string
            Type of the element added.
        uuid : str
            Identifier of the element in the GUI Manager. Must be unique.
        params : Dict[string, Any]
            Parametres of the element as a dictionary of pair keyword (string)
            to any type.

        Raises
        ------
        ValueError
            Element type given is not available.

        Returns
        -------
        None.

        """
        if self.app.DEBUG:
            print(f'Adding: {element_type}')
        try:
            self.__types_elements[element_type]
        except KeyError as error:
            raise ValueError(f'Type of Element: "{element_type}" does not exist.') from error

        new_element = self.__types_elements[element_type](
            self.app,
            uuid,
            **params
        )

        self.__add_element(new_element)

    def batch_add_elements(
            self,
            batch: dict[str, dict[str, Any]],
            parse: bool = True
    ):
        """
        Add a batch of Elements to the GUIManager.

        Parameters
        ----------
        batch : dict[string, dict[string, Any]]
            Batch must be a dictionary with keys as string being the uuid of
            the element and the value must be another dictionary containing
            keys as string where one mys be the type of the element ("class")
            and a dictionary with the paramenters of the element ("kwargs"),
            (result of reading a json file with the GUI layout),for example:
                batch = {
                    "uuid_1" : {
                        "class": "name_class",
                        "kwargs": {
                            "param_1": value_1,
                            "param_2": "value_2",
                            "param_3": [
                                "value_3",
                                "value_4",
                            ],
                            "param_4": {
                                "sub_param_1": value_5,
                                "sub_param_2": "value_6",
                            },
                        },
                    },
                    "uuid_2" : {
                        "class" : "name_class",
                        "kwargs": {
                            "param_1": value_1,
                            "param_2": "value_2",
                        },
                    },
                }
        parse : bool, optional
            If the keywords arguments must be parsed and autosized if they are
            not in the size petinent to the window. The default is True.

        Returns
        -------
        None.

        """
        for uuid, meta in batch.items():
            if parse:
                meta["kwargs"] = self._parse_kwargs(meta["kwargs"])

            self.add_element(meta['class'], uuid, meta['kwargs'])

    def check_click(self, mouse_position: tuple[int, int]) -> str | None:
        """
        Check actions when click event.

        Checks action when clicked and returns the uuid of the element that
        recived an action with the click or None if no element recived an
        action. Will return only one string of the first Element in order of
        addition found with an action.

        Parameters
        ----------
        mouse_position : tuple[integer, integer]
            Tuple with the (x, y) coordinate of the mouse in the window.

        Returns
        -------
        string or None
            Returns the UUID of the element that recived an action with the
            click or None if no element recived an action.

        """
        for element in self.__elements_buffer.values():
            click = element.check_click(mouse_position)
            if click:
                return click

        return None

    def check_hover(self, mouse_position: tuple[int, int]):
        """
        Check action when mouse hovering.

        Parameters
        ----------
        mouse_position : tuple[integer, integer]
            Tuple with the (x, y) coordinate of the mouse in the window.

        Returns
        -------
        None.

        """
        for element in self.__elements_buffer.values():
            element.check_hover(mouse_position)

    def check_unclick(self, mouse_position: tuple[int, int]) -> str | None:
        """
        Check actions when unclick event.

        Checks action when unclicked and returns the uuid of the element that
        recived an action with the unclick or None if no element recived an
        action. Will return only one string of the first Element in order of
        addition found with an action.

        Parameters
        ----------
        mouse_position : tuple[integer, integer]
            Tuple with the (x, y) coordinate of the mouse in the window.

        Returns
        -------
        None.
            Returns the UUID of the element that recived an action with the
            unclick or None if no element recived an action.

        """
        for element in self.__elements_buffer.values():
            unclick = element.check_unclick(mouse_position)
            if unclick:
                return unclick

        return None

    def destroy(self):
        """
        Destroy all the Elements and delete them from the GUIManager.

        Returns
        -------
        None.

        """
        for element in list(self.__elements_buffer.values()):
            element.destroy()
            del self.__elements_buffer[element.uuid]

    def hide(self):
        """
        Hides all Elements of the GUI.

        Returns
        -------
        None.

        """
        for element in self.__elements_buffer.values():
            element.hide()

    def lock(self):
        """
        Locks all the Elements of the GUI.

        Returns
        -------
        None.

        """
        for element in self.__elements_buffer.values():
            element.lock()

    def remove(self, uuid: str):
        """
        Remove a given Element from the GUI.

        Parameters
        ----------
        uuid : string
            UUID of the Element to remove.

        Raises
        ------
        ValueError
            The provided UUID has not been found in the GUI.

        Returns
        -------
        None.

        """
        try:
            self.__elements_buffer[uuid]
        except KeyError as error:
            raise ValueError(f'Element with uuid: "{uuid}" ' + 'does not exist.') from error

        self.__elements_buffer[uuid].destroy()
        del self.__elements_buffer[uuid]

    def render(self):
        """
        Render all visible Elements of the GUI.

        Returns
        -------
        None.

        """
        for element in self.__elements_buffer.values():
            element.render()

    def toggle(self):
        """
        Toggle all Elements of GUI.

        Returns
        -------
        None.

        """
        for element in self.__elements_buffer.values():
            element.toggle()

    def unhide(self):
        """
        Unhides all Elements of the GUI.

        Returns
        -------
        None.

        """
        for element in self.__elements_buffer.values():
            element.unhide()

    def unlock(self):
        """
        Unlocks all Elements of the GUI.

        Returns
        -------
        None.

        """
        for element in self.__elements_buffer.values():
            element.unlock()

    def untoggle(self):
        """
        Untoggles all Elements of the GUI.

        Returns
        -------
        None.

        """
        for element in self.__elements_buffer.values():
            element.untoggle()

###############################################################################


###############################################################################
#                                  Properties                                 #


    @property  # noqa
    def app(self):
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
        return None

    @property
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
        return None

    @property
    def is_locked(self) -> bool:
        """
        Return if Element is locked.

        Returns
        -------
        bool
            Is locked.

        """
        return None

    @property
    def uuid(self) -> str:
        """
        Return Element UUID.

        Returns
        -------
        str
            Element UUID.

        """
        return None

###############################################################################
