import glm
import math
import pygame as pg

class Camera:
    __slots__ = ["app", 
                 "aspec_ratio",
                 "position",
                 "up",
                 "yaw",
                 "pitch",
                 "sensitivity",
                 "speed",
                 "last_mouse_pos",
                 "left_button_held",
                 "m_view",
                 "m_proj"]
    """Classe que estableix la càmara en escena
    """
    def __init__(self, app):
        """Inicialització de la classe Camera

        Args:
            app (GraphicsEngine()): Instància de la classe GraphicsEngine()
        """
        self.app = app
        self.aspec_ratio = app.WIN_SIZE[0]/app.WIN_SIZE[1]
        self.position = glm.vec3(67.5445,26.7694,7.71201)
        self.up = glm.vec3(0,1,0)

        # Moviment de la càmera
        self.yaw, self.pitch = self.calculate_initial_orientation(self.position, glm.vec3(0, 0, 0))
        self.sensitivity = 0.1  # Mouse sensitivity for camera movement
        self.speed = 0.5  # Camera movement speed for WASD
        # Mouse control
        self.last_mouse_pos = None
        self.left_button_held = False

        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()
               
    def get_view_matrix(self):
        """
        Returns:
            glm.vec4: Matriu view 
        """
        # Calculate direction from yaw and pitch
        direction = glm.vec3()
        direction.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        direction.y = math.sin(glm.radians(self.pitch))
        direction.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        direction = glm.normalize(direction)

        return glm.lookAt(self.position, self.position + direction, self.up)
    
    def get_projection_matrix(self):
        """
        Returns:
            glm.vec4: Matriu projecció 
        """
        return glm.perspective(glm.radians(45), self.aspec_ratio, 0.1, 700)
    
    def calculate_initial_orientation(self, position, target):
        # Calculate the direction vector from the camera to the target
        direction = target - position

        # Calculate yaw (angle around the Y-axis)
        yaw = math.degrees(math.atan2(direction.z, direction.x))  # Yaw angle based on XZ-plane

        # Calculate pitch (angle around the X-axis)
        horizontal_dist = math.sqrt(direction.x ** 2 + direction.z ** 2)  # Distance on the XZ-plane
        pitch = math.degrees(math.atan2(direction.y, horizontal_dist))  # Pitch angle based on Y

        return yaw, pitch
    
    def process_mouse_movement(self, mouse_dx, mouse_dy):
        # Apply sensitivity and update yaw and pitch
        self.yaw += mouse_dx * self.sensitivity
        self.pitch -= mouse_dy * self.sensitivity

        # Constrain pitch (to avoid flipping the camera upside-down)
        self.pitch = max(-89.0, min(89.0, self.pitch))

        # Update the view matrix with new yaw and pitch
        self.m_view = self.get_view_matrix()
        for object in self.app.objects:
            object.faces_shader['m_view'].write(self.m_view)
    
    def process_keyboard(self):
        # Get the current key state
        keys = pg.key.get_pressed()

        # Forward and backward movement (W and S)
        if keys[pg.K_w]:
            self.move_forward(self.speed)
        if keys[pg.K_s]:
            self.move_forward(-self.speed)

        # Strafe left and right (A and D)
        if keys[pg.K_a]:
            self.strafe(-self.speed)
        if keys[pg.K_d]:
            self.strafe(self.speed)
    
    def move_forward(self, speed):
        # Calculate the forward direction based on yaw and pitch
        direction = glm.vec3()
        direction.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        direction.y = math.sin(glm.radians(self.pitch))
        direction.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        direction = glm.normalize(direction)

        # Update the camera position by moving along the forward direction
        self.position += direction * speed
        self.m_view = self.get_view_matrix()
        for object in self.app.objects:
            object.faces_shader['m_view'].write(self.m_view)
    
    def strafe(self, speed):
        # Strafe movement is based on the yaw only (moving perpendicular to the direction we're facing)
        right = glm.vec3()
        right.x = math.cos(glm.radians(self.yaw + 90))  # Perpendicular direction on the XZ plane
        right.z = math.sin(glm.radians(self.yaw + 90))
        right = glm.normalize(right)

        # Update the camera position by strafing
        self.position += right * speed
        self.m_view = self.get_view_matrix()
        for object in self.app.objects:
            object.faces_shader['m_view'].write(self.m_view)