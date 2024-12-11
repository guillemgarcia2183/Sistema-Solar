import glm
import math
import pygame as pg

from enum import Enum

class Camera:
    """Classe que estableix la càmara en escena
    """
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
                 "m_proj",
                 "minimum_speed",
                 "maximum_speed"]

    def __init__(self, app):
        """Inicialització de la classe Camera

        Args:
            app (GraphicsEngine()): Instància de la classe GraphicsEngine()
        """
        self.app = app
        self.aspec_ratio = app.WIN_SIZE[0]/app.WIN_SIZE[1]
        self.position = glm.vec3( 66.8807,      66.8807,      66.8807) # ---------Per què aquesta posició?
        self.up = glm.vec3(0,1,0)

        # Moviment de la càmera
        self.yaw, self.pitch = self.calculate_initial_orientation(self.position, glm.vec3(0, 0, 0))
        self.sensitivity = 0.1  # Mouse sensitivity for camera movement
        self.speed = 0.7  # Camera movement speed for WASD
        
        self.minimum_speed = 0.1
        self.maximum_speed = 20

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
        return glm.perspective(glm.radians(45), self.aspec_ratio, 0.1, 2000)
    
    def get_type(self):
        return "Camera"

    def change_lock(self):
        pass

    def follow_target(self):
        """Funció per seguir al objectiu
        """
        self.update_shaders_m_view()

    def calculate_initial_orientation(self, position, target):
        """Càlcul de l'orientació inicial de la càmera
        """
        # Calculate the direction vector from the camera to the target
        direction = target - position

        # Calculate yaw (angle around the Y-axis)
        yaw = math.degrees(math.atan2(direction.z, direction.x))  # Yaw angle based on XZ-plane

        # Calculate pitch (angle around the X-axis)
        horizontal_dist = math.sqrt(direction.x ** 2 + direction.z ** 2)  # Distance on the XZ-plane
        pitch = math.degrees(math.atan2(direction.y, horizontal_dist))  # Pitch angle based on Y

        return yaw, pitch
    
    def update_shaders_m_view(self):
        """Actualització de la matriu view dels objectes
        """
        # New m_view
        self.m_view = self.get_view_matrix()
        # Update all shaders
        for object in self.app.objects:
            object.shader['m_view'].write(self.m_view)
        for orbit in self.app.orbits:
            orbit.shader['m_view'].write(self.m_view)
        self.app.stars.shader['m_view'].write(self.m_view)
        self.app.stars.constellations_shader['m_view'].write(self.m_view)

    def process_mouse_movement(self, mouse_dx, mouse_dy):
        """Processar el moviment del ratolí
        """
        # Apply sensitivity and update yaw and pitch
        self.yaw += mouse_dx * self.sensitivity
        self.pitch -= mouse_dy * self.sensitivity

        # Constrain pitch (to avoid flipping the camera upside-down)
        self.pitch = max(-89.0, min(89.0, self.pitch))

        # Update the view matrix with new yaw and pitch
        self.update_shaders_m_view()
    
    def process_keyboard(self):
        """Actualitzar la càmera segons els events de l'aplicació (WASD, Space i Ctrl)
        """
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

        # Move upward (Spacebar) or downward (Control key)    
        if keys[pg.K_SPACE]:
            self.move_upward(self.speed)
        if keys[pg.K_LCTRL] or keys[pg.K_RCTRL]:  # Left or Right Control
            self.move_upward(-self.speed)
    
    def move_forward(self, speed):
        """Moure endevant la càmera

        Args:
            speed (float): Velocitat 
        """
        # Calculate the forward direction based on yaw and pitch
        direction = glm.vec3()
        direction.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        direction.y = math.sin(glm.radians(self.pitch))
        direction.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        direction = glm.normalize(direction)

        # Update the camera position by moving along the forward direction
        self.position += direction * speed
        self.update_shaders_m_view()

    def move_upward(self, speed):
        """Moure la càmera amunt

        Args:
            speed (float): Velocitat
        """
        # Calculate the forward direction based on yaw and pitch
        forward = glm.vec3(
            math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
            math.sin(glm.radians(self.pitch)),
            math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        )
        forward = glm.normalize(forward)

        # Calculate the right direction (strafe direction)
        right = glm.vec3(
            math.cos(glm.radians(self.yaw + 90)),
            0,
            math.sin(glm.radians(self.yaw + 90))
        )
        right = glm.normalize(right)

        # Calculate the upward direction relative to the camera
        upward = glm.cross(right, forward)
        upward = glm.normalize(upward)

        # Move the camera in the upward direction
        self.position += upward * speed

        # Update the view matrix for all objects and stars
        self.update_shaders_m_view()

    def strafe(self, speed):
        """Moviment lateral

        Args:
            speed (float): Velocitat
        """
        # Strafe movement is based on the yaw only (moving perpendicular to the direction we're facing)
        right = glm.vec3()
        right.x = math.cos(glm.radians(self.yaw + 90))  # Perpendicular direction on the XZ plane
        right.z = math.sin(glm.radians(self.yaw + 90))
        right = glm.normalize(right)

        # Update the camera position by strafing
        self.position += right * speed

        # Update the view matrix for all objects and stars
        self.update_shaders_m_view()

class FollowCamera(Camera):
    """Classe que estableix la càmara planetària
    """ 
    __slots__ = ("target", 
                 "elevation",
                 "azimuth",
                 "distance",
                 "lock_target",
                 "relative_position",
                 "right",
                 "keep_up",
                 "direction")
    
    def __init__(self, app):
        """
        Initializes the FollowCamera.

        Args:
            distance (float): The distance from the camera to the planet.
        """
        self.target = None
        self.elevation = 0
        self.azimuth = 0
        self.distance = 0
        self.lock_target = True
        self.relative_position = glm.vec3(1,0,0)
        self.right = glm.vec3(0,0,1)
        self.keep_up = True
        self.direction = glm.vec3(0,0,0)
        super().__init__(app)
        #self.sensitivity *= 0.01
    
    def get_type(self):
        return "FollowCamera"
    
    def change_lock(self):
        if self.lock_target:
            # Calculem la posició que estàvem amb lock_target
            self.elevation = glm.degrees(glm.asin(self.position.y / self.distance))
            delta_x = self.position.x - self.target.actual_pos.x
            delta_z = self.position.z - self.target.actual_pos.z
            self.azimuth = glm.degrees(glm.atan(delta_z, delta_x))
            # Canviem el mode
            self.lock_target = False
        else:
            self.relative_position = (self.position - self.target.actual_pos)/self.distance
            self.lock_target = True
        

    def get_view_matrix(self):
        """
        Sobrecarreguem aquesta funció per gestionar si volem que la càmera es fixi en el planeta o no
        Returns:
            glm.vec4: Matriu view 
        """

        if self.lock_target and self.target is not None: # Condició temporal, un cop el canvi de target estigui implementat s'haurà de canviar
            self.direction = glm.normalize(self.target.actual_pos - self.position)
            if self.keep_up: # Moviments AD, mantenim el vector 'up' per generar el vector 'right' en el pla desitjat
                self.right = glm.normalize(glm.cross(self.direction, self.up))
                # Recalculem 'up' per a que tenir la nova base
                self.up = glm.normalize(glm.cross(self.right, self.direction))

            else: # Moviments WS, mantenim el vector 'right' per generar el vector 'up' en el pla desitjat
                self.up = glm.normalize(glm.cross(self.right, self.direction))
                # Recalculem 'right' per a que tenir la nova base
                self.right = glm.normalize(glm.cross(self.direction, self.up))
                
            #print(f"right:{self.right}\nup:{self.up}")
            return glm.lookAt(self.position, self.position + self.direction, self.up)
        else:
            return glm.lookAt(self.position, self.position + self.direction, self.up)

    def select_target(self, target):
        """ ----RECORDATORI----
            SELECCIONAR TARGET 
            DESPRÉS DE CREAR-LOS
        """
        self.target = self.app.objects[self.app.objects_index[target]]
        self.distance = self.app.ideal_dists[target] + (3*self.target.radius)

        #print(f"distance: {self.distance}\n\nradius: {self.target.radius}")
        # TODO: calculate the speed so that it takes the same time to wrap around any planet
        if self.target.radius < 1:
            self.speed /= self.target.radius
        else:
            self.speed *= self.target.radius

    def synchronize_yaw_pitch(self):
        """Synchronize yaw and pitch with the current forward direction."""
        forward = glm.normalize(self.target.actual_pos - self.position)

        # Calculate yaw (atan2 gives us the angle in the XZ plane)
        self.yaw = glm.degrees(glm.atan(forward.z, forward.x)) % 360

        # Pitch is the vertical angle of the forward vector
        self.pitch = glm.degrees(glm.asin(forward.y / glm.length(forward)))
        
    def process_keyboard(self):
        # Get the current key state
        keys = pg.key.get_pressed()

        # Change the elevation relative to the object
        increment = glm.vec3(0, 0, 0)
        if keys[pg.K_w]:
            if self.lock_target:
                self.keep_up = False
                increment += self.up * 0.1##self.speed
            else:
                self.elevation = (self.elevation + self.speed) % 360
        if keys[pg.K_s]:
            if self.lock_target:
                self.keep_up = False
                increment -= self.up * 0.1#self.speed
            else:
                self.elevation = (self.elevation - self.speed) % 360
        if keys[pg.K_a]:
            if self.lock_target:
                self.keep_up = True
                increment -= self.right * 0.1#self.speed
            else:
                self.azimuth = (self.azimuth + self.speed) % 360
        if keys[pg.K_d]:
            if self.lock_target:
                self.keep_up = True
                increment += self.right * 0.1#self.speed
            else:
                self.azimuth = (self.azimuth - self.speed) % 360
                # Update the relative position
        if keys[pg.K_q]:  # Roll counterclockwise
            self.roll(-self.speed)
        if keys[pg.K_e]:  # Roll clockwise
            self.roll(self.speed)

        self.relative_position += increment

        # Normalize the relative position to stay on the sphere
        self.relative_position = glm.normalize(self.relative_position) 

    def process_mouse_movement(self, mouse_dx, mouse_dy):
        """Processar el moviment del ratolí quan no hi ha lock_target
        """
        if not self.lock_target:
            # Calculate rotation around the vertical axis (yaw) for horizontal movement
            yaw_rotation = glm.rotate(glm.mat4(1.0), glm.radians(-mouse_dx * self.sensitivity), self.up)
            self.direction = glm.normalize(glm.vec3(yaw_rotation * glm.vec4(self.direction, 0.0)))
            self.right = glm.normalize(glm.cross(self.direction, self.up))

            # Calculate rotation around the horizontal axis (pitch) for vertical movement
            pitch_rotation = glm.rotate(glm.mat4(1.0), glm.radians(-mouse_dy * self.sensitivity), self.right)
            new_direction = glm.normalize(glm.vec3(pitch_rotation * glm.vec4(self.direction, 0.0)))
            
            # Prevent flipping by clamping the pitch
            if abs(glm.dot(new_direction, self.up)) < 0.99:  # Limit pitch to near-horizontal
                self.direction = new_direction
                self.up = glm.normalize(glm.cross(self.right, self.direction))

            # Update the view matrix with the new direction, right, and up
            self.update_shaders_m_view()

    def roll(self, angle):
        rotation_matrix = glm.rotate(glm.mat4(1.0), glm.radians(angle), self.direction)

        # Apply the rotation to 'up' and 'right' vectors
        self.up = glm.normalize(glm.vec3(rotation_matrix * glm.vec4(self.up, 0.0)))
        self.right = glm.normalize(glm.vec3(rotation_matrix * glm.vec4(self.right, 0.0)))

        # Update the view matrix with the new 'up' and 'right' vectors
        self.update_shaders_m_view()

    def follow_target(self):
        """Update the camera's position based on the planet's position and the set distance and angles."""
        if not self.lock_target:
            x = self.target.actual_pos.x + self.distance * glm.cos(glm.radians(self.elevation)) * glm.cos(glm.radians(self.azimuth))
            y = self.distance * glm.sin(glm.radians(self.elevation)) # self.target.actual_pos.y serà sempre 0
            z = self.target.actual_pos.z + self.distance * glm.cos(glm.radians(self.elevation)) * glm.sin(glm.radians(self.azimuth))
            
            # Update camera position and direction
            self.position = glm.vec3(x, y, z)
        else:
            self.position = self.target.actual_pos + self.relative_position * self.distance

        self.update_shaders_m_view()
