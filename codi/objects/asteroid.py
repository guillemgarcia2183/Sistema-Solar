import random
import numpy as np
import glm
from objects.object import Object
from scipy.spatial import KDTree
import math

class AsteroidBatch(Object):
    """Crea el cinturó d'asteroides mitjançant instancing. Classe heretada de Object"""
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
               "collision_adjustments",
               "enabled")
    
    def __init__(self, app, shader, texture, info, num_asteroids, distance1, distance2, velocity, eccentricity, type, enable_collision=False):
        """
        Inicialització de la classe AsteroidBatch

        Args:
            num_asteroids (int): Nombre d'asteroides en el cinturó
            distance1 (float): Mínima distància del asteroide 
            distance2 (float): Màxima distància del asteroide
            velocity (float): Màxima velocitat dels asteroides
            eccentricity (float): Excentricitat de l'òrbita 
            type (str): Tipus d'asteroide (Trojan o Belt)
        """
        self.distance1 = distance1
        self.distance2 = distance2
        self.num_asteroids = num_asteroids
        self.velocity = velocity
        self.eccentricity = eccentricity
        self.type = type
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
        """Gemeració de la matriu que farà instancing

        Returns:
            np.darray: Array de matrius de models, cadascuna representant un asteroide
        """
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
                velocity = random.uniform(self.velocity/10, self.velocity)
            else:
                velocity = self.velocity

            y_asteroid = random.uniform(-6,6)
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
            scale_factor = random.uniform(0.1, 1)
            self.scales.append(scale_factor)  # Store the scale factor

            model = glm.scale(model, glm.vec3(scale_factor, scale_factor, scale_factor))

            matrices.append(np.array(model).T)  # Transpose for column-major order
        
        return np.array(matrices, dtype='f4')
        
    def update_orbit(self):
        """Actualitzar l'òrbita dels asteroides
        """
        updated_matrices = []
        new_positions = []
        for i in range(self.num_asteroids):
            # Retrieve current asteroid distance 
            distance = self.distances[i]

            # Calculate semi-major and semi-minor axes
            a = distance  # Semi-major axis
            b = a * (1 - self.eccentricity ** 2) ** 0.5  # Semi-minor axis
            angle = self.angles[i]
            # Increment the angle based on velocity and time
            angle += self.velocity_asteroids[i] * self.app.time  # Use velocity and time for orbit speed
            # angle %= 2*np.pi 

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
        """Actualitzar l'orbitació dels asteroides, comprovant si succeeix una col·lisió
        """
        if self.enabled:
            if (self.type == "Belt"):
                collisions = self.check_collisions_optimized()
                if len(collisions) > 0:
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
        """Posició inicial dels asteroides

        Returns:
            list: Posicions de cada asteroide al inici de l'aplicació
        """
        return [self.instance_matrices[i][3][:3] for i in range(self.num_asteroids)]
    
    def find_neighbors(self, asteroid):
        """Trobar els k veïns més propers del asteroide

        Args:
            asteroid (glm.vec3): Asteroide a comprovar els veïns

        Returns:
            (list, list): Llista dels índexos i distàncies dels veïns més propers
        """
        # Comprovar si està construït el kd_tree
        kd_tree = KDTree(self.positions)
        #Consultar els k veïns més propers del asteroides 
        distances, indices = kd_tree.query(asteroid, k=2)
        #Retorna els índexs de self.positions que té més propers (ignorant ell mateix)
        return indices[1:], distances[1:]
    
    def check_collisions(self):
        """Comprovar si es produeix una col·lisió amb tots els asteroides

        Returns:
            list[Tuple]: Índexos dels asteroides que han col·lisionat
        """
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
                if (distance**2) <= ((radius_asteroid + radius_neighbor)**2):
                    collisions.append([index, n])  # Guardem els índexs dels asteroides que col·lisionen
        return collisions
    
    def check_collisions_optimized(self):
        positions = np.array(self.positions)
        radius = np.array(self.scales)*self.radius

        # Coordenadas separades per calcular distàncies
        p1 = positions[:,0].reshape(-1,1)
        p2 = positions[:,1].reshape(-1,1)
        p3 = positions[:,2].reshape(-1,1)

        # Calculem sumatori de distàncies  
        distance = (p1 - p1.transpose())**2
        distance += (p2 - p2.transpose())**2
        distance += (p3 - p3.transpose())**2
        np.fill_diagonal(distance, math.inf)

        # Calcular las distancias de colisión permitidas
        collision_distance = (radius + radius.reshape(-1, 1)) ** 2

        # Identificar colisiones: matriz booleana
        collisions_mask = distance <= collision_distance

        # Extraer los pares de índices donde ocurre colisión
        collisions_indices = np.argwhere(collisions_mask)
        
        # Evitar duplicats
        collisions_indices = collisions_indices[collisions_indices[:, 0] < collisions_indices[:, 1]]

        return collisions_indices

    def apply_collision(self, collisions, adjustment_amount=0.1):
        """Aplicar la col·lisió als asteroides en qüestió

        Args:
            collisions (list[Tuple]): Llista dels asteroides que han col·lisionat
            adjustment_amount (float, optional): Angle a adjustar dels asteroides. Defaults to 0.1.
        """
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
        """Aplicar el adjustament del angle dels asteroides mitjançant diversos frames 
        """
        smoothing_factor_angle = 0.001
        for key, a in self.collision_adjustments.items():
            if a != 0:
                adjustment = smoothing_factor_angle * np.sign(a)

                if abs(adjustment) > abs(a):
                   adjustment = a 
                
                self.angles[key] += adjustment

                self.collision_adjustments[key] -= adjustment

                if (self.collision_adjustments[key] - adjustment) == 0:
                    if adjustment < 0:
                        self.velocity_asteroids[key] *= 0.99
                    elif adjustment > 0:
                        self.velocity_asteroids[key] *= 1.01
    

