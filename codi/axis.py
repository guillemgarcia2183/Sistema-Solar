import glm
import moderngl as mgl
import numpy as np

class Axis:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program()
        self.vao = self.get_vao()
        self.m_model = glm.mat4()
        self.on_init()

    def on_init(self):
        self.shader_program['m_proj'].write(self.app.camera.m_proj)
        self.shader_program['m_view'].write(self.app.camera.m_view)
        self.shader_program['m_model'].write(self.m_model)

    def render(self):
        self.ctx.line_width = 1.0
        self.vao.render(mgl.LINES)

    def destroy(self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()

    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, '3f 3f', 'in_position', 'in_color')])
        return vao

    def get_vertex_data(self):
        scale = 5.0
        vertices = [(0, 0, 0, 1, 0, 0), (scale, 0, 0, 1, 0, 0), (0, 0, 0, 0, 1, 0), (0, scale, 0, 0, 1, 0), (0, 0, 0, 0, 0, 1), (0, 0, scale, 0, 0, 1)]
        return np.array(vertices, dtype='f4')

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo

    def get_shader_program(self):
        program = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec3 in_position;
                in vec3 in_color;
                out vec3 v_color;
                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;
                void main() {
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                    v_color = in_color;
                }
            ''',
            fragment_shader='''
                #version 330
                in vec3 v_color;
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(v_color, 1.0);
                }
            ''',
        )
        return program