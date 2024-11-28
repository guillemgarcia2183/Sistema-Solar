import glm
import math
import pygame as pg

from enum import Enum

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
        self.position = glm.vec3( 66.8807,      66.8807,      66.8807) # ---------Per què aquesta posició?
        self.up = glm.vec3(0,1,0)

        # Moviment de la càmera
        self.yaw, self.pitch = self.calculate_initial_orientation(self.position, glm.vec3(0, 0, 0))
        self.sensitivity = 0.1  # Mouse sensitivity for camera movement
        self.speed = 0.7  # Camera movement speed for WASD
        
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

    def follow_target(self):
        pass

    def calculate_initial_orientation(self, position, target):
        # Calculate the direction vector from the camera to the target
        direction = target - position

        # Calculate yaw (angle around the Y-axis)
        yaw = math.degrees(math.atan2(direction.z, direction.x))  # Yaw angle based on XZ-plane

        # Calculate pitch (angle around the X-axis)
        horizontal_dist = math.sqrt(direction.x ** 2 + direction.z ** 2)  # Distance on the XZ-plane
        pitch = math.degrees(math.atan2(direction.y, horizontal_dist))  # Pitch angle based on Y

        return yaw, pitch
    
    def update_shaders_m_view(self):
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
        # Apply sensitivity and update yaw and pitch
        self.yaw += mouse_dx * self.sensitivity
        self.pitch -= mouse_dy * self.sensitivity

        # Constrain pitch (to avoid flipping the camera upside-down)
        self.pitch = max(-89.0, min(89.0, self.pitch))

        # Update the view matrix with new yaw and pitch
        self.update_shaders_m_view()
    
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

        # Move upward (Spacebar) or downward (Control key)    
        if keys[pg.K_SPACE]:
            self.move_upward(self.speed)
        if keys[pg.K_LCTRL] or keys[pg.K_RCTRL]:  # Left or Right Control
            self.move_upward(-self.speed)
    
    def move_forward(self, speed):
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
        # Strafe movement is based on the yaw only (moving perpendicular to the direction we're facing)
        right = glm.vec3()
        right.x = math.cos(glm.radians(self.yaw + 90))  # Perpendicular direction on the XZ plane
        right.z = math.sin(glm.radians(self.yaw + 90))
        right = glm.normalize(right)

        # Update the camera position by strafing
        self.position += right * speed

        # Update the view matrix for all objects and stars
        self.update_shaders_m_view()

class Planets(Enum):
    SUN     = 0
    MERCURY = 1 
    VENUS   = 3
    EARTH   = 5
    MART    = 7
    JUPITER = 9
    SATURN  = 11
    URANUS  = 13
    NEPTUNE = 15

class PlanetaryCamera():

    def __init__(self, app: object, 
                 planet: int = Planets.JUPITER,
                 height_of_camera: float = 10.0):
         
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0]/app.WIN_SIZE[1]
        self.planet = planet.value
        self.height = height_of_camera
        self.position = self.app.objects[self.planet].position \
                            + glm.vec3(0, self.height, 0)
        self.up = glm.vec3(0, 1, 0)

        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()
               
    def get_view_matrix(self) -> glm.mat4x4:
        # For now let's look at the sun
        # TODO: Sun has NO position artibute wich makes no sense
        return glm.lookAt(self.position, glm.vec3(0), self.up)
    
    def get_projection_matrix(self) -> glm.mat4x4:
        return glm.perspective(glm.radians(45), self.aspect_ratio, 0.1, 700)

    def update(self) -> None:
        """Rotació dela camara sobre el sol.
        """
        
        planet = self.app.objects[self.planet]

        # Semieje mayor y menor basados en la distancia inicial del planeta al Sol
        a = glm.length(glm.vec2(planet.position.x, planet.position.z))  # La magnitud en XZ como semieje mayor
        b = a * (1 - planet.excentrity ** 2) ** 0.5 # Semieje menor (ajústalo según el grado de excentricidad que desees)

        # Calcular el ángulo en función del tiempo
        theta = self.app.time * planet.velocity   # Ajusta la velocidad de la órbita

        # Posición del planeta en la órbita elíptica (plano XZ)
        x = a * glm.cos(theta)
        z = b * glm.sin(theta)
        y = 0

        # Trasladar el planeta a la nueva posición calculada (órbita elíptica respecto al Sol en (0, 0, 0))
        new_position = glm.vec3(x, y, z)
        self.position = new_position + glm.vec3(0, self.height, 0)
        self.m_view = self.get_view_matrix()

        for object in self.app.objects:
            object.faces_shader['m_view'].write(self.m_view)

    def process_keyboard(self):
        pass

class FollowCamera(Camera):
    __slots__ = ["target", 
                 "elevation",
                 "azimuth",
                 "distance",
                 "lock_target",
                 "relative_position",
                 "right",
                 "keep_up"]
    """Classe que estableix la càmara planetària
    """ 
    def __init__(self, app, distance, lock_target = True):
        """
        Initializes the FollowCamera.

        Args:
            distance (float): The distance from the camera to the planet.
        """
        self.target = None
        self.elevation = 0
        self.azimuth = 0
        self.distance = distance
        self.lock_target = lock_target
        self.relative_position = glm.vec3(1,0,0)
        self.right = glm.vec3(0,0,1)
        self.keep_up = True
        super().__init__(app)
    
    def get_type(self):
        return "FollowCamera"
                 
    def get_view_matrix(self):
        """
        Sobrecarreguem aquesta funció per gestionar si volem que la càmera es fixi en el planeta o no
        Returns:
            glm.vec4: Matriu view 
        """

        if self.lock_target and self.target is not None: # Condició temporal, un cop el canvi de target estigui implementat s'haurà de canviar
            """
            direction = glm.normalize(self.target.actual_pos - self.position)
            
            preliminary_up = glm.cross(preliminary_up, forward)

            # Ensure up is perpendicular to forward
            #right = glm.normalize(glm.cross(preliminary_up, forward))
            self.up = glm.normalize(preliminary_up)
                    
            return glm.lookAt(self.position, self.target.actual_pos, self.up)
            
            direction = glm.normalize(self.target.actual_pos - self.position)
            
            # Create quaternion for azimuth and elevation rotation
            azimuth_quat = glm.angleAxis(glm.radians(self.azimuth), glm.vec3(0, 1, 0))  # Y-axis rotation
            elevation_quat = glm.angleAxis(glm.radians(self.elevation), glm.vec3(1, 0, 0))  # X-axis rotation

            # Combine rotations
            rotation_quat = azimuth_quat * elevation_quat

            # Rotate world up vector (0, 1, 0) to calculate the camera's up vector. We use self.up since it is already defined as we want
            new_up = glm.normalize(rotation_quat * self.up * (1/rotation_quat))

            # Ensure self.up is perpendicular to direction
            right = glm.normalize(glm.cross(new_up, direction))
            self.up = glm.normalize(glm.cross(direction, right))

            # Return the view matrix
            return glm.lookAt(self.position, self.target.actual_pos, self.up)
        """
            direction = glm.normalize(self.target.actual_pos - self.position)
            if self.keep_up: # Moviments AD, mantenim el vector 'up' per generar el vector 'right' en el pla desitjat
                self.right = glm.normalize(glm.cross(direction, self.up))
                # Recalculem 'up' per a que tenir la nova base
                self.up = glm.normalize(glm.cross(self.right, direction))

            else: # Moviments WS, mantenim el vector 'right' per generar el vector 'up' en el pla desitjat
                self.up = glm.normalize(glm.cross(self.right, direction))
                # Recalculem 'right' per a que tenir la nova base
                self.right = glm.normalize(glm.cross(direction, self.up))
                
            #print(f"right:{self.right}\nup:{self.up}")
            return glm.lookAt(self.position, self.position + direction, self.up)
        else:
            return super().get_view_matrix()

    def select_target(self, target):
        """ ----RECORDATORI----
            SELECCIONAR TARGET 
            DESPRÉS DE CREAR-LOS
        """
        self.target = target
        # TODO: calculate the speed so that it takes the same time to wrap around any planet
        if self.target.radius < 1:
            self.speed /= target.radius
        else:
            self.speed *= target.radius 
    
    def process_keyboard(self):
        # Get the current key state
        keys = pg.key.get_pressed()

        # Change the elevation relative to the object 
        """
        if keys[pg.K_w]:
            #self.elevation = (self.elevation + self.speed) % 360
            self.keep_up = False
            self.relative_position.x = self.relative_position.x + glm.normalize(self.speed * (self.right.x + self.up.x))
            self.relative_position.y = self.relative_position.y + glm.normalize(self.speed * (self.right.y + self.up.y))
            self.relative_position.z = self.relative_position.z + glm.normalize(self.speed * (self.right.z + self.up.z))
        if keys[pg.K_s]:
            #self.elevation = (self.elevation - self.speed) % 360
            self.keep_up = False
            self.relative_position.x = self.relative_position.x - glm.normalize(self.speed * (self.right.x + self.up.x))
            self.relative_position.y = self.relative_position.y - glm.normalize(self.speed * (self.right.y + self.up.y))
            self.relative_position.z = self.relative_position.z - glm.normalize(self.speed * (self.right.z + self.up.z))

        # Change the azimuth relative to the object
        if keys[pg.K_a]:
            #self.azimuth = (self.azimuth + self.speed) % 360
            self.keep_up = True
            self.relative_position.x = self.relative_position.x + glm.normalize(self.speed * (self.right.x + self.up.x))
            self.relative_position.y = self.relative_position.y + glm.normalize(self.speed * (self.right.y + self.up.y))
            self.relative_position.z = self.relative_position.z + glm.normalize(self.speed * (self.right.z + self.up.z))
        if keys[pg.K_d]:
            #self.azimuth = (self.azimuth - self.speed) % 360
            self.keep_up = True
            self.relative_position.x = self.relative_position.x - glm.normalize(self.speed * (self.right.x + self.up.x))
            self.relative_position.y = self.relative_position.y - glm.normalize(self.speed * (self.right.y + self.up.y))
            self.relative_position.z = self.relative_position.z - glm.normalize(self.speed * (self.right.z + self.up.z))
        """
        increment = glm.vec3(0, 0, 0)
        if keys[pg.K_w]:
            self.keep_up = False
            increment += self.up * 0.1##self.speed
        if keys[pg.K_s]:
            self.keep_up = False
            increment -= self.up * 0.1#self.speed
        if keys[pg.K_a]:
            self.keep_up = True
            increment -= self.right * 0.1#self.speed 
        if keys[pg.K_d]:
            self.keep_up = True
            increment += self.right * 0.1#self.speed

        # Update the relative position
        self.relative_position += increment

        # Normalize the relative position to stay on the sphere
        self.relative_position = glm.normalize(self.relative_position) 
        
    def follow_target(self):
        """Update the camera's position based on the planet's position and the set distance and angles."""
        """# Calculate Cartesian coordinates from spherical
        x = self.target.actual_pos.x + self.distance * glm.cos(glm.radians(self.elevation)) * glm.cos(glm.radians(self.azimuth))
        y = self.distance * glm.sin(glm.radians(self.elevation)) # self.target.actual_pos.y serà sempre 0
        z = self.target.actual_pos.z + self.distance * glm.cos(glm.radians(self.elevation)) * glm.sin(glm.radians(self.azimuth))
        
        # Update camera position and direction
        self.position = glm.vec3(x, y, z)
        """
        
        self.position = self.target.actual_pos + self.relative_position * self.distance
        print(f"Target actual pos:{self.target.actual_pos}")
        print(f"Camera relative pos:{self.relative_position}")
        print(f"Camera pos:{self.position}")
        self.update_shaders_m_view()
