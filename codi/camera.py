import glm
import math

class Camera:
    def __init__(self, app):
        self.app = app
        self.aspec_ratio = app.WIN_SIZE[0]/app.WIN_SIZE[1]
        self.position = glm.vec3(8,3,0)
        self.up = glm.vec3(0,1,0)
        self.angle = 0
        self.t0 = 0
        self.angular_speed = -1.15
        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()
               
    def get_view_matrix(self):
        return glm.lookAt(self.position, glm.vec3(0), self.up)
    
    def get_projection_matrix(self):
        return glm.perspective(glm.radians(45), self.aspec_ratio, 0.1, 100)
    
    def update(self):
        delta_time = self.app.time - self.t0
        self.t0 = self.app.time
        self.angle = (self.angle + self.angular_speed*delta_time) % (2*math.pi) # Adjust the angle over time to simulate movement
        x = 7 * math.cos(self.angle)
        z = 7 * math.sin(self.angle)
        self.position = glm.vec3(x, 7, z) 

        # Update the view matrix to reflect the new position
        self.m_view = glm.lookAt(self.position, glm.vec3(0), self.up)
        self.app.object.faces_shader['m_view'].write(self.m_view)
        self.app.object.edges_shader['m_view'].write(self.m_view)
        self.app.axis.shader_program['m_view'].write(self.m_view)