import random
import numpy as np
import glm
from objects.object import Object
from scipy.spatial import KDTree

class AsteroidBatch(Object):
    """Class to create an asteroid belt using instancing."""
    __slots__=("distance1",
               "distance2",
               "num_asteroids",
               "velocity",
               "eccentricity",
               "distances",
               "scales",
               "angles",
               "velocity_asteroids",
               "y_asteroids",
               "instance_matrices",
               "instance_buffer",
               "type",
               "positions",
               "mass",
               "collision_adjustments",
               "enabled")
    def __init__(self, app, shader, texture, info, num_asteroids, distance1, distance2, velocity, eccentricity, type, enable_collision=False):
        """
        Initialize the Asteroid class.

        Args:
            num_asteroids (int): Number of asteroids in the belt.
            distance1 (float): Minimum distance for the asteroid.
            distance2 (float): Maximum distance for the asteroid.
            velocity (float): Maximum velocity of the asteroids 
            eccentricity (float): Eccentricity of the asteroid belt
            type (str): Type of asteroids (Belt or Trojan)
        """
        self.distance1 = distance1
        self.distance2 = distance2
        self.num_asteroids = num_asteroids
        self.velocity = velocity
        self.eccentricity = eccentricity
        self.type = type
        self.mass = 1.0        
        super().__init__(app, shader, texture, info) 

        # Generate instance-specific transformation matrices
        self.instance_matrices = self.generate_instance_matrices()
        self.instance_buffer = self.ctx.buffer(self.instance_matrices.astype('f4').tobytes())
        
        # Update the VAO to include the instance buffer
        self.vao = self.ctx.vertex_array(
            self.shader,
            [
                (self.vbo, '3f 3f 2f', 'in_norm', 'in_position', 'in_tex_coord'),
                (self.instance_buffer, '16f/i', 'instance_model'),
            ],
        )

        self.positions = self.initial_positions()
        self.collision_adjustments = {}
        self.enabled = enable_collision

    def on_init(self):
        """Pos-inicialització de la classe Object. Establiment dels paràmetres del shader 
        """
        # Related to lighting
        self.shader['light.position'].write(self.app.light.position)
        self.shader['view_pos'].write(self.app.camera.position)
        self.shader['light.Ia'].write(self.app.light.Ia)
        self.shader['light.Id'].write(self.app.light.Id)
        self.shader['light.Is'].write(self.app.light.Is)

        # Essential for viewing
        self.shader['m_proj'].write(self.app.camera.m_proj)
        self.shader['m_view'].write(self.app.camera.m_view)      

    def generate_instance_matrices(self):
        """Generate transformation matrices for all asteroid instances."""
        matrices = []
        self.distances = []
        self.scales = []
        self.angles = []
        self.velocity_asteroids=[]
        self.y_asteroids = []

        for _ in range(self.num_asteroids):
            # Ensure the distance is between Mars and Jupiter
            distance = random.uniform(self.distance1, self.distance2)
            if self.type == "Belt":
                velocity = random.uniform(self.velocity/4, self.velocity)
            else:
                velocity = self.velocity

            y_asteroid = random.uniform(-5,5)
            self.distances.append(distance)  # Store the distance
            self.velocity_asteroids.append(velocity)
            self.y_asteroids.append(y_asteroid)

            # Generate a random initial angle for orbit
            if self.type == "Belt":
                angle = random.uniform(0, 2 * np.pi)
            elif self.type == "Trojan Right":
                angle = (np.pi / 3) + random.uniform(-0.5, 0.5)  
            else:
                angle = (-np.pi / 3) + random.uniform(-0.5, 0.5)  

            self.angles.append(angle)
            
            # Calculate semi-major and semi-minor axes
            a = distance  # Semi-major axis (distance from the Sun)
            b = a * (1 - self.eccentricity ** 2) ** 0.5  # Semi-minor axis
        
            # Calculate position in orbit
            x = a * np.cos(angle)
            z = b * np.sin(angle)
            y = y_asteroid  # You can adjust this if you want inclined orbits

            # Create the transformation matrix
            model = glm.mat4(1.0)
            model = glm.translate(model, glm.vec3(x, y, z))  # Position in orbit
            scale_factor = random.uniform(0.25, 1)
            self.scales.append(scale_factor)  # Store the scale factor

            model = glm.scale(model, glm.vec3(scale_factor, scale_factor, scale_factor))

            matrices.append(np.array(model).T)  # Transpose for column-major order
        
        return np.array(matrices, dtype='f4')
        
    def update_orbit(self):
        """Update the orbit of each asteroid based on velocity and time."""
        updated_matrices = []
        new_positions = []
        for i in range(self.num_asteroids):
            # Retrieve current asteroid distance 
            distance = self.distances[i]

            # Calculate semi-major and semi-minor axes
            a = distance  # Semi-major axis
            b = a * (1 - self.eccentricity ** 2) ** 0.5  # Semi-minor axis
            angle = float(self.angles[i])
            # Increment the angle based on velocity and time
            angle += self.velocity_asteroids[i] * self.app.time  # Use velocity and time for orbit speed
            #angle %= 2*np.pi 
            # Update position based on the new angle
            x = float(a * np.cos(angle))
            z = float(b * np.sin(angle))
            y = float(self.y_asteroids[i])  # You can adjust this if needed

            new_positions.append([x, y, z])  # Store the new position

            # Create the new transformation matrix
            model = glm.mat4(1.0)
            model = glm.translate(model, glm.vec3(x, y, z))  # Position in orbit
            scale_factor = self.scales[i]  # Use the stored scale factor
            model = glm.scale(model, glm.vec3(scale_factor, scale_factor, scale_factor))

            updated_matrices.append(np.array(model).T)

        # Update the instance buffer with the new matrices
        self.instance_buffer.write(np.array(updated_matrices, dtype='f4').tobytes())
        # Update the positions array with the new positions
        self.positions = new_positions
        
    def move(self):
        if self.enabled:
            if (self.type == "Belt"):
                collisions = self.check_collisions()
                if collisions:
                    #print(f"Collisions detected: {collisions}, number of collisions:{len(collisions)}")
                    self.apply_collision(collisions)

            self.smooth_angle_adjustments()
        self.update_orbit()

    def render(self):
        """Renderització del VAO
        """
        self.texture.use()
        self.vao.render(instances=self.num_asteroids)

    def get_data(self):
        """Genera esfera (asteroides)"""
        return self.create_sphere(False)
    
    def initial_positions(self):
        return [self.instance_matrices[i][3][:3] for i in range(self.num_asteroids)]
    
    def find_neighbors(self, asteroid):
        # Comprovar si està construït el kd_tree
        kd_tree = KDTree(self.positions)
        #Consultar els k veïns més propers del asteroides 
        distances, indices = kd_tree.query(asteroid, k=2)
        #Retorna els índexs de self.positions que té més propers (ignorant ell mateix)
        return indices[1:], distances[1:]
    
    def check_collisions(self):
        collisions = []
        checked_pairs = set() 
        # Iterem tots els asteroides
        for index, asteroid in enumerate(self.positions):
            # Trobem els més propers
            neighbors, distances = self.find_neighbors(asteroid)
            radius_asteroid = self.scales[index]*self.radius
            for i,n in enumerate(neighbors):
                # Evita repetir la comprovació de la parella (index, n)
                if (index, n) in checked_pairs or (n, index) in checked_pairs:
                    continue
                # Marcar la parella com comprovada
                checked_pairs.add((index, n))
                # Paràmetres del veï (distance, radius)
                radius_neighbor = self.scales[n]*self.radius
                distance = distances[i]
                # Comprova si hi ha col·lisió
                if distance <= (radius_asteroid + radius_neighbor):
                    collisions.append((index, n))  # Guardem els índexs dels asteroides que col·lisionen
        return collisions
    
    def apply_collision(self, collisions, adjustment_amount=0.1):
        for (i1, i2) in collisions:
            velocity1 = self.velocity_asteroids[i1]
            velocity2 = self.velocity_asteroids[i2]

            if i1 not in self.collision_adjustments:
                self.collision_adjustments[i1] = 0.0
            if i2 not in self.collision_adjustments:
                self.collision_adjustments[i2] = 0.0
            
            if velocity1 > velocity2:
                self.collision_adjustments[i1] -= adjustment_amount
                self.collision_adjustments[i2] += adjustment_amount
            else:
                self.collision_adjustments[i1] += adjustment_amount
                self.collision_adjustments[i2] -= adjustment_amount

    def smooth_angle_adjustments(self):
        smoothing_factor = 0.001
        for key, a in self.collision_adjustments.items():
            if a != 0:
                adjustment = smoothing_factor * np.sign(a)

                if abs(adjustment) > abs(a):
                   adjustment = a 
                
                self.angles[key] += adjustment

                self.collision_adjustments[key] -= adjustment

                # # if (self.collision_adjustments[key]) == 0:
                # #     if adjustment < 0:
                # #         self.velocity_asteroids[key] *= 0.9
                # #     elif adjustment > 0:
                # #         self.velocity_asteroids[key] *= 1.1
                    