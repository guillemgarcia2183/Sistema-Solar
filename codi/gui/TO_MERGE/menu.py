class Menu:
    def __init__(self, app, button_manager, uuid, meta):
        """
        Initialize a menu with toggle and additional buttons.

        Parameters:
        - app: The GraphicsEngine instance.
        - button_manager: ButtonManager instance.
        - uuid: Unique identifier for the menu.
        - meta: Dictionary containing menu layout and button properties.
        """
        self.app = app
        self.button_manager = button_manager
        self.uuid = uuid
        self.is_visible = True
        self.buttons = []

        # Add the toggle button
        toggle_button_config = meta["toggle_button"]
        toggle_button_uuid = f"{uuid}_toggle"
        toggle_button_config["uuid"] = f"{uuid}_toggle"
        button_manager.add_button(
            "rectangular", toggle_button_uuid, {k: v for k, v in toggle_button_config.items() if k != "uuid"})
        
        self.toggle_button_uuid = toggle_button_config["uuid"]

        # Add other menu buttons
        for button_id, button_config in meta["buttons"].items():
            button_uuid = f"{uuid}_{button_id}"
            button_config["uuid"] = button_uuid  # Set UUID directly in config
            self.buttons.append(button_uuid)
            button_manager.add_button(
                button_config["class"], button_uuid, {k: v for k, v in button_config.items() if k != "uuid"}
            )

    def toggle_visibility(self):
        """
        Toggle visibility of the menu buttons.
        """
        self.is_visible = not self.is_visible
        if self.is_visible:
            for button_uuid in self.buttons:
                self.button_manager._ButtonManager__buttons_buffer[button_uuid].unhide()
        else:
            for button_uuid in self.buttons:
                self.button_manager._ButtonManager__buttons_buffer[button_uuid].hide()

        # Update toggle button text
        #toggle_button = self.button_manager._ButtonManager__buttons_buffer[self.toggle_button_uuid]
        #toggle_button.__text = {"text": "<" if self.is_visible else ">", "color": (0.0, 0.0, 0.0), "font_size": 24}

    def check_click(self, mouse_position):
        """
        Check for clicks on menu buttons or the toggle button.
        """
        # Check if the toggle button is clicked
        toggle_button = self.button_manager._ButtonManager__buttons_buffer[self.toggle_button_uuid]
        if toggle_button.check_click(mouse_position):
            self.toggle_visibility()
            return self.toggle_button_uuid

        # Check other buttons
        for button_uuid in self.buttons:
            button = self.button_manager._ButtonManager__buttons_buffer[button_uuid]
            if button.check_click(mouse_position):
                return button_uuid
        return None

    def check_hover(self, mouse_position):
        """
        Check for hover events on menu buttons.
        """
        for button_uuid in self.buttons:
            button = self.button_manager._ButtonManager__buttons_buffer[button_uuid]
            button.check_hover(mouse_position)

    def render(self):
        """
        Render the menu buttons.
        """
        for button_uuid in self.buttons:
            button = self.button_manager._ButtonManager__buttons_buffer[button_uuid]
            button.render()
        toggle_button = self.button_manager._ButtonManager__buttons_buffer[self.toggle_button_uuid]
        toggle_button.render()
