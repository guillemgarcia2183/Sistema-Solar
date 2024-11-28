# -*- coding: utf-8 -*- noqa
"""
Created on Thu Oct 24 13:09:18 2024

@author: Joel Tapia Salvador
"""
import moderngl
import numpy as np
import pygame as pg


class TextLabel:

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
        "__vao",
        "__vbo",
        "__vertexes",
        "__width",
        "__x",
        "__y",
    )

    def __init__(self, app, uuid: str, **kwargs):
        default_kwargs = {
            'text': "",
            'x': 0,
            'y': 0,
            'color': (1.0, 1.0, 1.0),
            'sys_font': 'Arial',
            'font_size': 12,
            'scale_factor': 2,
        }

        kwargs = default_kwargs | kwargs  # NOTE: Works for python 3.9+

        print(kwargs)

        # Engine
        self.__app = app

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
        self.__set_shader_programs()

        # Create all ModernGL objects
        self.__set_vao()

    def __set_text_texture(self):
        # Set font
        self.__set_font()

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
        texture = self.__app.ctx.texture(
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

    def __set_font(self):
        # Load Pygame font object from system font
        self.__font = pg.font.SysFont(
            self.__sys_font,
            self.__font_size * self.__scale_factor,
        )

    def __set_shader_programs(self) -> moderngl.Program:
        """
        Generate the shader program that will render this object.

        Returns
        -------
        program : moderngl Program
            Shader Program.

        """
        self.__shader_programs = self.__app.ctx.program(
            vertex_shader='''
            #version 330
            in vec2 in_position;
            in vec2 in_texcoord;

            out vec2 v_texcoord;

            void main() {
                v_texcoord = in_texcoord;
                gl_Position = vec4(in_position, 1.0, 1.0);
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

    def __set_vao(self):
        """
        Set the vao of the object.

        Calls to set the vbo before it.

        Returns
        -------
        None.

        """
        self.__set_vbo()

        self.__vao = self.__app.ctx.simple_vertex_array(
            self.__shader_programs,
            self.__vbo,
            'in_position',
            'in_texcoord',
        )

    def __set_vbo(self):
        """
        Set the vbo of the object.

        Calls to set the vertexes before it.

        Returns
        -------
        None.

        """
        self.__set_vertexes()

        self.__vbo = self.__app.ctx.buffer(self.__vertexes.tobytes())

    def __set_vertexes(self):
        # Set text texture
        self.__set_text_texture()

        gl_x = (
            2 * (
                (
                    self.__x - (self.__width / 2) -
                    (self.__app.WIN_SIZE[0] / 2)
                ) / (
                    self.__app.WIN_SIZE[0]
                )
            ),
            2 * (
                (
                    self.__x + (self.__width / 2) -
                    (self.__app.WIN_SIZE[0] / 2)
                ) / (
                    self.__app.WIN_SIZE[0]
                )
            )
        )

        gl_y = (
            -2 * (
                (
                    self.__y - (self.__height / 2) -
                    (self.__app.WIN_SIZE[1] / 2)
                ) / (
                    self.__app.WIN_SIZE[1]
                )
            ),
            -2 * (
                (
                    self.__y + (self.__height / 2) -
                    (self.__app.WIN_SIZE[1] / 2)
                ) / (
                    self.__app.WIN_SIZE[1]
                )
            )
        )

        self.__vertexes = np.array(
            [
                gl_x[0], gl_y[0], 0.0, 1.0,
                gl_x[1], gl_y[0], 1.0, 1.0,
                gl_x[0], gl_y[1], 0.0, 0.0,
                gl_x[1], gl_y[1], 1.0, 0.0,
            ],
            dtype='f4'
        )

    def destroy(self):
        """
        Destroy moderngl object to free memory when deleting.

        Returns
        -------
        None.

        """
        self.__vbo.destroy()

        self.__vao.destroy()

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
