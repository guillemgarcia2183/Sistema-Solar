# -*- coding: utf-8 -*- noqa
"""
Created on Thu Oct 24 13:09:18 2024

@author: Joel Tapia Salvador
"""

if __name__ == "__main__":
    raise SystemExit(
        'You are executing a package-module file.' +
        ' Execute a main instead and import the module.')


import moderngl
import numpy as np
import pygame as pg


class TextLabel():

    __slots__ = (
        "__app",
        "__color",
        "__font",
        "__font_size",
        "__height",
        "__scale_factor",
        "__shader_programs",
        "__sys_font",
        "__text",
        "__texture",
        "__uuid",
        "__vao",
        "__vbo",
        "__vertexes",
        "__width",
        "__x",
        "__y",
    )

###############################################################################
#                             Overloaded Operators                            #

    def __init__(self, app, uuid: str, **kwargs):
        default_kwargs = {
            'text': "",
            'x': 0,
            'y': 0,
            'color': (0.0, 0.0, 0.0),
            'sys_font': 'Arial',
            'font_size': 12,
            'scale_factor': 2,
        }

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        # Engine
        self.__app = app

        # Text Labels's unique id
        self.__uuid = uuid

        if self.app.DEBUG:
            print("Text Label")
            print(kwargs)

        # Font information
        self.__font_size = kwargs['font_size']
        self.__scale_factor = kwargs['scale_factor']
        self.__sys_font = kwargs['sys_font']

        # Text information
        self.__color = kwargs['color']
        self.__text = kwargs['text']
        self.__x = kwargs['x']
        self.__y = kwargs['y']

        # Write the shader
        self._set_shader_programs()

        # Create all ModernGL objects
        self._set_vao()

###############################################################################


###############################################################################
#                               Private Methods                               #


    def _set_font(self):  # noqa
        # Load Pygame font object from system font
        self.__font = pg.font.SysFont(
            self.__sys_font,
            self.__font_size * self.__scale_factor,
        )

    def _set_shader_programs(self) -> moderngl.Program:
        """
        Generate the shader program that will render this object.

        Returns
        -------
        program : moderngl Program
            Shader Program.

        """
        self.__shader_programs = self.app.ctx.program(
            vertex_shader='''
            #version 330

            in vec2 in_position;
            in vec2 in_texcoord;

            out vec2 v_texcoord;

            void main() {
                v_texcoord = in_texcoord;
                gl_Position = vec4(in_position, 0.0, 1.0);
            }
            ''',
            fragment_shader='''
            #version 330

            in vec2 v_texcoord;

            uniform sampler2D text_texture;

            out vec4 frag_color;

            void main() {
                vec4 tex_color = texture(text_texture, v_texcoord);
                if (tex_color.a < 0.1) {
                   discard; // Discard transparent pixels
                }

                frag_color = tex_color;
            }
            '''
        )

        if self.app.DEBUG:
            print("Shader program compiled and linked successfully.")

    def _set_text_texture(self):
        # Set font
        self._set_font()

        # Render Pygame text
        text = self.__font.render(
            self.__text,
            True,
            (
                self.__color[0] * 255,
                self.__color[1] * 255,
                self.__color[2] * 255,
                255,
            )
        )

        # Flip Pygame text vertically
        text = pg.transform.flip(
            text, False, True)

        # Transform text into bytes
        bytes_text = pg.image.tobytes(text, 'RGBA', True)

        # Get size of the text
        text_width, text_height = text.get_size()

        # Transform into a ModernGL texture
        texture = self.app.ctx.texture(
            (text_width, text_height),
            4,
            bytes_text,
        )

        # Use linear filtering for smoother text
        texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

        texture.build_mipmaps()

        # Set text texture parameters in object
        self.__width = text_width // self.__scale_factor
        self.__height = text_height // self.__scale_factor
        self.__texture = texture

        # Bind texture
        self.__texture.use()

        if self.app.DEBUG:
            print(f"Rendering text: '{self.__text}'")
            print(f"Text size: {self.__font.size(self.__text)}")
            print(f"Text surface size: {text.get_size()}")
            print(f"Bytes length: {len(bytes_text)}")

    def _set_vao(self):
        """
        Set the vao of the object.

        Calls to set the vbo before it.

        Returns
        -------
        None.

        """
        self._set_vbo()

        if self.app.DEBUG:
            print("Program attributes:",
                  self.__shader_programs._attribute_locations)

        self.__vao = self.app.ctx.simple_vertex_array(
            self.__shader_programs,
            self.__vbo,
            'in_position',
            'in_texcoord',
        )

    def _set_vbo(self):
        """
        Set the vbo of the object.

        Calls to set the vertexes before it.

        Returns
        -------
        None.

        """
        self._set_vertexes()

        bytes_vertex = self.vertexes.tobytes()

        if self.app.DEBUG:
            print(bytes_vertex)

        self.__vbo = self.app.ctx.buffer(bytes_vertex)

        if self.app.DEBUG:
            print(self.app.ctx.buffer)

    def _set_vertexes(self):
        # Set text texture
        self._set_text_texture()

        ndc_x_center = (self.x / self.app.WIN_SIZE[0]) * 2 - 1
        ndc_y_center = -((self.y / self.app.WIN_SIZE[1]) * 2 - 1)

        # Half-width and half-height in NDC
        ndc_half_w = self.width / self.app.WIN_SIZE[0]
        ndc_half_h = self.height / self.app.WIN_SIZE[1]

        # Define quad vertices centered at (ndc_x_center, ndc_y_center)
        self.__vertexes = np.array([
            # Position                  # Texcoords
            ndc_x_center - ndc_half_w, ndc_y_center - ndc_half_h,
            0.0, 1.0,  # Bottom-left
            ndc_x_center + ndc_half_w, ndc_y_center - ndc_half_h,
            1.0, 1.0,  # Bottom-right
            ndc_x_center - ndc_half_w, ndc_y_center + ndc_half_h,
            0.0, 0.0,  # Top-left
            ndc_x_center + ndc_half_w, ndc_y_center + ndc_half_h,
            1.0, 0.0,  # Top-right
        ], dtype='f4')

        # self.__vertexes = np.array([
        #     # Position        # Texcoords
        #     -0.5, -0.5,  # 0.0, 1.0,  # Bottom-left
        #     0.5, -0.5,  # 1.0, 1.0,  # Bottom-right
        #     -0.5,  0.5,  # 0.0, 0.0,  # Top-left
        #     0.5,  0.5,  # 1.0, 0.0,  # Top-right
        # ], dtype='f4')

        if self.app.DEBUG:
            print(f"Vertices (NDC): {self.vertexes}")

###############################################################################


###############################################################################
#                                Public Methods                               #

    def destroy(self):  # noqa
        """
        Destroy moderngl object to free memory when deleting.

        Returns
        -------
        None.

        """
        self.__texture.release()

        self.__vbo.release()

        self.__vao.release()

        self.__shader_programs.release()

    def render(self):
        """
        Render the vao.

        Returns
        -------
        None.

        """
        # Bind texture
        self.__texture.use()

        self.__vao.render(moderngl.TRIANGLE_STRIP)

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
    def font(self) -> str:
        return self.__sys_font

    @font.setter
    def font(self, new_font: str):
        self.__sys_font = new_font
        self._set_vao()

    @property
    def font_size(self) -> int:
        return self.__font_size

    @font_size.setter
    def font_size(self, new_font_size: int):
        self.__font_size = new_font_size
        self._set_vao()

    @property
    def height(self) -> int:
        return self.__height

    @property
    def scale_factor(self) -> int:
        return self.__scale_factor

    @scale_factor.setter
    def scale_factor(self, new_scale_factor: int):
        self.__scale_factor = new_scale_factor
        self._set_vao()

    @property
    def text_color(self) -> tuple[float, float, float]:
        return self.__color

    @text_color.setter
    def text_color(self, new_color: tuple[float, float, float]):
        self.__color = new_color
        self._set_vao()

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

    @property
    def vertexes(self):
        return self.__vertexes

    @property
    def width(self) -> int:
        return self.__width

    @property
    def x(self) -> int:
        return self.__x

    @x.setter
    def x(self, new_x: int):
        self.__x = new_x

        self._set_vao()

    @property
    def y(self) -> int:
        return self.__y

    @y.setter
    def y(self, new_y: int):
        self.__y = new_y

        self._set_vao()

###############################################################################
