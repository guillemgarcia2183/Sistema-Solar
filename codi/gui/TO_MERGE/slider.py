import moderngl as mgl
import numpy as np
from typing import Tuple

class Slider:
    def __init__(self, app, uuid: str, **kwargs):
        """
        Create a slider.

        Parameters:
        - app: The application instance.
        - uuid: Unique identifier for the slider.
        - x, y: Position of the slider (centered).
        - width, height: Dimensions of the slider track.
        - min_value: Minimum value of the slider.
        - max_value: Maximum value of the slider.
        - initial_value: Starting value of the slider.
        - track_color: Color of the slider track.
        - handle_color: Color of the slider handle.
        - hover_color: Color of the handle when hovered.
        """
        default_kwargs = { 'x': 0, 'y': 0, 'width': 0, 'height': 0,
                 'min_value':0, 'max_value':4, 'initial_value':2, 'track_color':(0.8, 0.8, 0.8),
                 'handle_color':(0.5, 0.5, 0.5), 'hover_color':(0.6, 0.6, 0.6), "is_hidden": False}
        
        kwargs = {**default_kwargs, **kwargs}

        self.app = app
        self.uuid = uuid

        # Extract general slider attributes
        self.x = kwargs["x"]
        self.y = kwargs["y"]
        self.width = kwargs["width"]
        self.height = kwargs["height"]
        self.slices = kwargs["slices"]

        # Extract slider range and initial value
        self.min_value = kwargs["min_value"]
        self.max_value = kwargs["max_value"]

        # Extract colors
        self.track_color = kwargs["track_color"]
        self.handle_color = kwargs["handle_color"]
        self.hover_color = kwargs["hover_color"]

        # Interaction states
        self.is_hovered = False
        self.is_dragging = False
        self.__is_hidden = kwargs["is_hidden"]

        dif = self.max_value - self.min_value
        self.handle_values = [self.min_value + i*dif/(self.slices-1) for i in range(self.slices)]
        self.current_slice = self.slices//2
        # OpenGL setup
        self.shader_programs = self.__create_shader_programs()
        self.track_vao = self.__create_track_vao()
        self.handle_vao = self.__create_handle_vao()

    def __create_shader_programs(self):
        """
        Create the shader programs for rendering the slider.
        """
        return self.app.ctx.program(
            vertex_shader='''
            #version 330
            layout (location = 0) in vec3 in_vert;
            void main() {
                gl_Position = vec4(in_vert, 1.0);
            }
            ''',
            fragment_shader='''
            #version 330
            uniform vec3 in_color;
            out vec4 frag_color;
            void main() {
                frag_color = vec4(in_color, 1.0);
            }
            '''
        )

    def __create_track_vao(self):
        """
        Create the VAO for the slider track.
        """
        gl_x = (
            2 * ((self.x - (self.width / 2) - (self.app.WIN_SIZE[0] / 2) - self.width / self.slices) / (self.app.WIN_SIZE[0])),
            2 * ((self.x + (self.width / 2) - (self.app.WIN_SIZE[0] / 2) + self.width / self.slices) / (self.app.WIN_SIZE[0]))
        )

        gl_y = (
            -2 * ((self.y - (self.height / 2) - (self.app.WIN_SIZE[1] / 2)) / (self.app.WIN_SIZE[1])),
            -2 * ((self.y + (self.height / 2) - (self.app.WIN_SIZE[1] / 2)) / ( self.app.WIN_SIZE[1]))
        )

        track_vertices = np.array(
            [
                gl_x[0], gl_y[0], 0.0,
                gl_x[1], gl_y[0], 0.0,
                gl_x[0], gl_y[1], 0.0,
                gl_x[1], gl_y[1], 0.0,
            ],
            dtype='f4'
        )
        vbo = self.app.ctx.buffer(track_vertices.tobytes())
        return self.app.ctx.vertex_array(self.shader_programs, [(vbo, '3f', 'in_vert')])

    def __create_handle_vao(self):
        """
        Create the VAO for the slider handle.
        """
        handle_x = self.__value_to_position()
        
        handle_vertices = np.array([
            self.__to_gl_x(handle_x - self.width / self.slices), self.__to_gl_y(self.y - self.height / 2), 0.0,
            self.__to_gl_x(handle_x + self.width / self.slices), self.__to_gl_y(self.y - self.height / 2), 0.0,
            self.__to_gl_x(handle_x - self.width / self.slices), self.__to_gl_y(self.y + self.height / 2), 0.0,
            self.__to_gl_x(handle_x + self.width / self.slices), self.__to_gl_y(self.y + self.height / 2), 0.0,
        ], dtype='f4')
        vbo = self.app.ctx.buffer(handle_vertices.tobytes())
        return self.app.ctx.vertex_array(self.shader_programs, [(vbo, '3f', 'in_vert')])

    def __to_gl_x(self, x):
        """
        Convert x position to OpenGL normalized device coordinates.
        """
        return 2*(x - self.app.WIN_SIZE[0] / 2) / (self.app.WIN_SIZE[0])

    def __to_gl_y(self, y):
        """
        Convert y position to OpenGL normalized device coordinates.
        """
        return -2*(y - self.app.WIN_SIZE[1] / 2) / (self.app.WIN_SIZE[1])

    def __value_to_position(self):
        """
        Map a slider value to a screen position.
        """
        return self.x - self.width / 2 + (self.handle_values[self.current_slice] - self.min_value) / (self.max_value - self.min_value) * self.width

    def render(self):
        """
        Render the slider.
        """
        if self.__is_hidden:
            return None
        # Render track
        self.shader_programs['in_color'].value = self.track_color
        self.track_vao.render(mgl.TRIANGLE_STRIP)

        # Render handle
        self.shader_programs['in_color'].value = self.hover_color if self.is_hovered else self.handle_color
        self.handle_vao.render(mgl.TRIANGLE_STRIP)

    def destroy(self) -> None:
        self.handle_vao.release()

        self.track_vao.release()

        self.shader_programs.release()

    def hide(self):
        self.__is_hidden = True

    def check_click(self, mouse_pos):
        """
        Check if the slider is clicked and begin dragging if necessary.
        """
        mx, my = mouse_pos
        handle_x = self.__value_to_position()
        if abs(mx - handle_x) <= self.width / 2 and abs(my - self.y) <= self.height / 2:
            self.is_dragging = True
            return True
        return False
    
    def check_hover(self, mouse_pos: Tuple[int, int]) -> None:
        pass
    
    def update_value(self, mouse_x):
        """
        Update the slider value based on mouse x position.
        """
        
        if self.is_dragging:
            new_value = self.min_value + (mouse_x - (self.x - self.width / 2)) / self.width * (self.max_value - self.min_value)
            self.current_slice = min(range(len(self.handle_values)), key=lambda i: abs(self.handle_values[i] - new_value))
            self.handle_vao = self.__create_handle_vao()
            #print(f"mouse X: {mouse_x}\tnew_value: {new_value}")
        return self.handle_values[self.current_slice]
    
    def release(self):
        """
        Stop dragging when mouse button is released.
        """
        self.is_dragging = False
