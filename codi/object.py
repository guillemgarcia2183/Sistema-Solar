import glm
import numpy as np
import moderngl as mgl
import os
from PIL import Image
import math
import random

class Object:
    __slots__ = (
        "app",
        "ctx",
        "texture",
        "method",
        "lat",
        "lon",
        "subdivisions",
        "vbo",
        "shader",
        "vao",
        "m_model",
        "radius",
    )
    
    """Classe per crear un objecte dintre del Sistema Solar (classe pare)
    """
    def __init__(self, app, shader, texture, info):
        """Inicialització de la classe Object

        Args:
            app (GraphicsEngine()): Instància de la classe GraphicsEngine()
            shader (list): Llista que conté el vertex_shader i fragment_shader a utilitzar 
            texture (str): Path de l'imatge que texturitzarem l'objecte
            info (list, optional): Informació per crear les esferes (en cas de planetes i sol). Defaults to ["octahedron", 3].
        """
        #App variables
        self.app = app
        self.ctx = app.ctx
        
        #Sphere parameters
        self.radius = info[0]
        self.lat = info[1]
        self.lon = info[2]

        # Object variables
        self.texture = self.load_texture(texture)
        self.vbo = self.get_vbo()
        self.shader = self.get_shader_program(shader)
        self.vao = self.get_vao()
        self.m_model = self.get_model_matrix()

        #Shader initialization
        self.on_init()

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
        self.shader['m_model'].write(self.m_model)

    def load_texture(self, filepath):
        """Carregar la textura d'entrada 

        Args:
            filepath (str): Path on està la imatge a texturitzar l'objecte

        Returns:
            mgl.texture: Textura
        """
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        image = Image.open(filepath).transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT)
        texture = self.ctx.texture(image.size, 3, image.tobytes())
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()
        texture.repeat_x = False
        texture.repeat_y = False
        return texture

    def get_vbo(self):
        """Obtenció del VBO 

        Returns:
            moderngl.VertexArray: Array VBO
        """
        data = self.get_data()
        vbo = self.ctx.buffer(data)
        return vbo
    
    def destroy(self):
        """Neteja de les variables després d'acabar l'execució del programa
        """
        self.vbo.release()
        self.shader.release()
        self.texture.release()
        self.vao.release()    

    def get_vao(self):
        """Obtenció del VAO 

        Returns:
            moderngl.VertexArray: Array VAO
        """
        vao = self.ctx.vertex_array(self.shader,[(self.vbo, '3f 3f 2f', 'in_norm', 'in_position', 'in_tex_coord')])
        return vao

    def create_sphere(self, sun):
        """Crear esfera per coordenades esfèriques

        Returns:
            np.array: Vector de coordenades (normal, position, texture)
        """
        data = []
        vertices = []
        indices = []
        
        # Latitude and longitude angles in radians
        for lat in range(self.lat + 1):
            theta = np.pi * lat / self.lat
            for lon in range(self.lon + 1):  # Increase by 1 to close the loop
                phi = 2 * np.pi * lon / self.lon
                
                # Spherical to Cartesian conversion
                x = self.radius * np.sin(theta) * np.cos(phi)
                y = self.radius * np.cos(theta)
                z = self.radius * np.sin(theta) * np.sin(phi)
                
                # Calculate texture coordinates with improved wrap handling
                s = lon / self.lon
                t = 1 - (lat / self.lat)
                
                vertices.append((x, y, z, s, t))
        
        # Create faces (triangles) between vertices (latitude-longitude stripes)
        for lat in range(self.lat):
            for lon in range(self.lon):
                current = lat * (self.lon + 1) + lon
                next = current + self.lon + 1
                
                # Triangles for the quad strip
                indices.append((current, next, current + 1))
                indices.append((current + 1, next, next + 1))

        for face in indices:
            for idx in face:
                x, y, z, s, t = vertices[idx]
                vertex = glm.vec3(x, y, z)
                normalized_v = self.normalize(vertex)
                
                # Add vertex data
                #data.extend([self.color.x, self.color.y, self.color.z])  # in_color
                if sun:
                    data.extend([-normalized_v.x, -normalized_v.y, -normalized_v.z])  # Case: Sun
                else:
                    data.extend([normalized_v.x, normalized_v.y, normalized_v.z])  # Case: Others
                data.extend([vertex.x, vertex.y, vertex.z])  # in_position
                data.extend([s, t])  # Texture coordinates

        return np.array(data, dtype='f4')

    @staticmethod
    def normalize(v):
        """Normalitza un vèrtex 

        Args:
            v (list): Vèrtex amb valors (x,y,z)

        Returns:
            list: Vèrtex normalitzat en cada posició
        """
        norm = np.linalg.norm(v)
        return v / norm

    def get_shader_program(self, shader):
        """Obtenció del shader program 

        Args: 
            shader (list): Valors de vertex_shader i fragment_shader

        Returns:
            moderngl.Program: Programa que establim com serà el procediment del vertex shader i fragment shader 
        """
        program = self.ctx.program(vertex_shader= shader[0], fragment_shader= shader[1])
        return program
    
class Sun(Object): 
    """Classe filla d'Objecte. Crea el Sol. Es caracteritza per tenir les normals invertides de signe (per termes d'il·luminació)
    """
    def get_model_matrix(self):
        """Obtenció de la model matrix
        Returns:
            glm.vec4: Matriu model 
        """
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        return m_model

    def render(self):
        """Renderització del VAO
        """
        self.texture.use()
        self.vao.render()

    def get_data(self):
        return self.create_sphere(True)

class Planet(Object):
    __slots__=["size",
               "position",
               "velocity",
               "inclination",
               "excentrity"]
    
    """Classe filla d'Objecte. Crea els Planetes.
    """
    def __init__(self, app, shader, texture, info, size, position, velocity, inclination, excentrity):
        """Inicialització de la classe Planet. Tindrà els atributs de Object i els següents

        Args:
            size (glm.vec3): Tamany del planeta
            position (glm.vec3): Posició del planeta
            velocity (float): Velocitat del planeta
            inclination (float): Inclinació de rotació
            excentrity (float): Excentritat de l'el·lipse
        """
        # Característiques de l'esfera
        self.size = size
        self.position = position
        self.velocity = velocity
        self.inclination = inclination
        self.excentrity = excentrity
        super().__init__(app, shader, texture, info)
        
    def get_model_matrix(self):
        """Obtenció de la model matrix
        Returns:
            glm.vec4: Matriu model 
        """
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        m_model = glm.scale(m_model, self.size)  
        m_model = glm.translate(m_model, self.position)   
        return m_model
            
    def get_data(self):
        return self.create_sphere(False)
    
    def render(self):
        """Renderització del VAO i rotació dels planetes
        """
        self.texture.use()
        self.rotate_sun()
        self.rotate_self()
        self.vao.render()    

    def rotate_self(self):
        """Rotació del planeta sobre sí mateix.
        """        
        # Inclinación en el eje de rotación (por ejemplo, ligeramente inclinada)
        inclination_radians = math.radians(self.inclination)
        inclined_axis = glm.vec3(math.sin(inclination_radians), math.cos(inclination_radians), 0)

        # Normalizar el eje para que el vector tenga longitud 1
        inclined_axis = glm.normalize(inclined_axis)

        self.m_model = glm.rotate(self.m_model, self.app.time*self.velocity*20, inclined_axis)
        self.shader['m_model'].write(self.m_model)
        
    def rotate_sun(self):
        """Rotació del planeta sobre el sol.
        """
        # Crear una matriz de transformación inicial (identidad)
        m_model = glm.mat4()

        # Semieje mayor y menor basados en la distancia inicial del planeta al Sol
        a = glm.length(glm.vec2(self.position.x, self.position.z))  # La magnitud en XZ como semieje mayor
        b = a * (1 - self.excentrity ** 2) ** 0.5 # Semieje menor (ajústalo según el grado de excentricidad que desees)

        # Calcular el ángulo en función del tiempo
        theta = self.app.time * self.velocity   # Ajusta la velocidad de la órbita

        # Posición del planeta en la órbita elíptica (plano XZ)
        x = a * glm.cos(theta)
        z = b * glm.sin(theta)
        y = self.position.y  # Mantener la altura constante o ajustarla si deseas órbitas inclinadas

        # Trasladar el planeta a la nueva posición calculada (órbita elíptica respecto al Sol en (0, 0, 0))
        new_position = glm.vec3(x, y, z)

        m_model = glm.translate(m_model, new_position)
        m_model = glm.scale(m_model, self.size)
        
        # Actualizar la matriz de modelo
        self.m_model = m_model    

class Satellite(Object):
    __slots__=["size", "position", "distance_to_planet", "velocity_planet", "velocity_satellite", "inclination", "excentrity"]
    
    """Classe filla d'Objecte. Crea els Satèl·lits naturals.
    """
    def __init__(self, app, shader, texture, info, size, position, distance_to_planet, velocity_planet, velocity_satellite, inclination, excentrity):
        """Inicialització de la classe Planet. Tindrà els atributs de Object i els següents

        Args:
            size (glm.vec3): Tamany del satèl·lit
            position (glm.vec3): Posició del satèl·lit 
            velocity (float): Velocitat del satèl·lit
        """
        # Característiques de l'esfera
        self.size = size
        self.position = position
        self.distance_to_planet = distance_to_planet
        self.velocity_planet = velocity_planet
        self.velocity_satellite = velocity_satellite
        self.inclination = inclination
        self.excentrity = excentrity
        super().__init__(app, shader, texture, info)
        
    def get_model_matrix(self):
        """Obtenció de la model matrix
        Returns:
            glm.vec4: Matriu model 
        """
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        m_model = glm.scale(m_model, self.size)  
        m_model = glm.translate(m_model, self.position)   
        return m_model
            
    def get_data(self):
        return self.create_sphere(False)
    
    def render(self):
        """Renderització del VAO i rotació dels planetes
        """
        self.texture.use()
        planet_position = self.rotate_sun()
        self.rotate_planet(planet_position)
        self.rotate_self()
        self.vao.render()    

    def rotate_self(self):
        """Rotació del satèl·lit sobre sí mateix.
        """        
        # Inclinación en el eje de rotación (por ejemplo, ligeramente inclinada)
        inclination_radians = math.radians(self.inclination)
        inclined_axis = glm.vec3(math.sin(inclination_radians), math.cos(inclination_radians), 0)

        # Normalizar el eje para que el vector tenga longitud 1
        inclined_axis = glm.normalize(inclined_axis)

        self.m_model = glm.rotate(self.m_model, self.app.time*self.velocity_planet*20, inclined_axis)
        self.shader['m_model'].write(self.m_model)
    
    def rotate_planet(self, planet_position):
        """Rotació del satèl·lit sobre el planeta.
        """
        a = glm.length(glm.vec2(self.distance_to_planet, self.distance_to_planet))
        b = a * (1 - self.excentrity ** 2) ** 0.5  # Excentricidad de la órbita del satélite
        theta = self.app.time * self.velocity_satellite

        # Calcular la posición en la órbita alrededor del planeta (eje XZ)
        x = a * glm.cos(theta)
        z = b * glm.sin(theta)
        y = 0  # Mantén la órbita en el plano XZ o ajusta para órbitas inclinadas
        
        # Posición del satélite relativa al planeta
        satellite_position = glm.vec3(x, y, z) + planet_position

        # Aplicar la transformación de la órbita alrededor del planeta
        self.m_model = glm.translate(glm.mat4(), satellite_position)
        self.m_model = glm.scale(self.m_model, self.size)

    def rotate_sun(self):
        """Rotació del satèl·lit sobre el sol (igual que els planetes).
        """
        a = glm.length(glm.vec2(self.position.x, self.position.z))
        b = a * (1 - self.excentrity ** 2) ** 0.5
        theta = self.app.time * self.velocity_planet

        # Calcular la posición en la órbita elíptica (eje XZ) respecto al Sol
        x = a * glm.cos(theta)
        z = b * glm.sin(theta)
        y = self.position.y

        # Posición de la órbita alrededor del Sol
        planet_position = glm.vec3(x, y, z)
        
        return planet_position  # Devolver la posición del planeta

class Orbit(Object):
    __slots__=["position", "excentrity"]

    """Classe filla d'Objecte. Crea les òrbites dels planetes (traça el·lipses del seu moviment).
    """
    def __init__(self, app, shader, texture, info, position, excentrity):
        """Inicialització de la classe Orbit

        Args:
            position (glm.vec3): Posició del planeta
            excentrity (float): Excentritat de l'el·lipse
        """
        self.position = position
        self.excentrity = excentrity
        super().__init__(app, shader, texture, info)

    def on_init(self):
        """Post-inicialització de la classe Orbit.
        """
        self.shader['m_proj'].write(self.app.camera.m_proj)
        self.shader['m_view'].write(self.app.camera.m_view)
        self.shader['m_model'].write(self.m_model)
        orbit_color = glm.vec3(1.0, 1.0, 1.0)  # RGB blanc
        self.shader['orbit_color'].write(orbit_color)

    def get_vao(self):
        """Obtenció VAO òrbites
        """
        return self.ctx.vertex_array(self.shader, [(self.vbo, '3f', 'in_position')])
    
    def get_model_matrix(self):
        """
        Returns:
            glm.vec4: Matriu model 
        """
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        return m_model

    def update(self):
        self.shader['m_view'].write(self.app.camera.m_view)

    def render(self):
        """Renderització del VAO
        """
        self.update()
        self.vao.render(mgl.LINE_LOOP) 


    def get_data(self, num_points = 200):
        """Genera els punts de la òrbita del planeta al voltant del sol.
    
        Args:
            num_points (int): Nombre de punts a traçar l'el·lipse
        
        Returns:
            np.array: Array amb els punts de la òrbita
        """
        # Paràmetres de la òrbita
        a = glm.length(glm.vec2(self.position.x, self.position.z))  # Semieix major
        b = a * (1 - self.excentrity ** 2) ** 0.5  # Semieix menor

        orbit_points = []

        for i in range(num_points):
            theta = 2 * np.pi * i / num_points  # Ángulo en radianes
            x = a * np.cos(theta)
            z = b * np.sin(theta)
            orbit_points.append((x, 0, z))

        return np.array(orbit_points, dtype='f4')
    
class StarBatch(Object):
    __slots__ = (
        "positions", 
    )
    
    """Classe filla d'Objecte. Crea les estrelles que envoltarà tot el Sistema Solar.
    """
    def __init__(self, app, shader, texture, info, positions):
        """Inicialització de la classe StarBatch

        Args:
            positions (glm.vec3): Posició en l'espai de l'estrella 
        """
        self.positions = positions
        super().__init__(app, shader, texture, info)
    
    def get_vao(self):
        """Obtenció del VAO 

        Returns:
            moderngl.VertexArray: Array VAO
        """
        vao = self.ctx.vertex_array(self.shader,[(self.vbo, '3f 3f', 'in_color', 'in_position')])

        return vao
    def on_init(self):
        """Post-inicialització de la classe StarBatch
        """
        # Essential for viewing
        self.shader['m_proj'].write(self.app.camera.m_proj)
        self.shader['m_view'].write(self.app.camera.m_view)
        self.shader['m_model'].write(self.m_model)
    
    def get_color_from_mag(self, mag):
        """
        Mapea la magnitud de la estrella a un color.
        Las estrellas más brillantes (magnitudes bajas) serán de color blanco,
        y las más tenues (magnitudes altas) se acercarán a colores más oscuros.
        """
        # Definimos un rango de magnitudes y un rango de colores
        min_mag = -1.44  # Máxima luminosidad
        max_mag = 21   # Mínima luminosidad visible (estrellas más tenues)

        # Interpolamos entre 1.0 (blanco) y un valor más bajo (oscuro)
        intensity = (max_mag - mag) / (max_mag - min_mag)  # Intensidad proporcional a la magnitud
        color = glm.vec3(intensity, intensity, intensity)  # Generamos un color gris, entre blanco y gris oscuro

        return color

    def get_model_matrix(self):
        """Obtenció del model_matrix
        """
        # NOTE: Order of operations is from last -> first

        # in-world placement of the star
        rads = glm.radians(23.44)
        #m_model *= glm.translate(self.position) #TODO: Is this correct?
        m_model = glm.translate(-self.app.objects[1].position)
        m_model *= glm.rotate(glm.mat4(), rads, glm.vec3(0, 0, 1))

        return m_model
    
    def update(self):
        """Actualització de la càmera al moure-la
        """
        self.shader['m_view'].write(self.app.camera.m_view)

    def render(self):
        """Renderització de l'estrella
        """
        self.update()
        self.ctx.enable(mgl.PROGRAM_POINT_SIZE)
        self.ctx.point_size = 3
        self.vao.render(mgl.POINTS)

    def get_data(self):
        """Obtenció de les dades per generar el VBO

        Returns:
            np.array: Coordenades de les estrelles (position)
        """
        #data = np.array([self.position.x, self.position.y, self.position.z], dtype='f4')
        data = []
        for x,z,y,mag in self.positions:
            color = self.get_color_from_mag(mag)
            data.append((color.x, color.y, color.z, x, y, z))
        data = np.array(data, dtype='f4')
        return data

class AsteroidBatch(Object):
    """Class to create an asteroid belt using instancing."""
    
    def __init__(self, app, shader, texture, info, num_asteroids, mars_distance, jupiter_distance, velocity, eccentricity):
        """
        Initialize the Asteroid class.

        Args:
            num_asteroids (int): Number of asteroids in the belt.
            mars_distance (float): Minimum distance for the asteroid belt (distance of Mars).
            jupiter_distance (float): Maximum distance for the asteroid belt (distance of Jupiter).
        """
        self.mars_distance = mars_distance
        self.jupiter_distance = jupiter_distance
        self.num_asteroids = num_asteroids
        self.velocity = velocity
        self.eccentricity = eccentricity
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

    def get_model_matrix(self):
        """Obtenció de la model matrix
        Returns:
            glm.vec4: Matriu model 
        """
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        return m_model

    def generate_instance_matrices(self):
        """Generate transformation matrices for all asteroid instances."""
        matrices = []
        self.distances = []
        self.scales = []
        for _ in range(self.num_asteroids):
            # Ensure the distance is between Mars and Jupiter
            distance = random.uniform(self.mars_distance, self.jupiter_distance)
            self.distances.append(distance)  # Store the distance
            # Generate a random initial angle for orbit
            angle = random.uniform(0, 2 * np.pi)
            # Calculate semi-major and semi-minor axes
            a = distance  # Semi-major axis (distance from the Sun)
            b = a * (1 - self.eccentricity ** 2) ** 0.5  # Semi-minor axis

            # Calculate position in orbit
            x = a * np.cos(angle)
            z = b * np.sin(angle)
            y = 0  # You can adjust this if you want inclined orbits

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
        for i in range(self.num_asteroids):
            # Retrieve current asteroid distance and velocity
            distance = self.distances[i]

            # Calculate semi-major and semi-minor axes
            a = distance  # Semi-major axis
            b = a * (1 - self.eccentricity ** 2) ** 0.5  # Semi-minor axis

            # Increment the angle based on velocity and time
            theta = self.velocity * self.app.time  # Use velocity and time for orbit speed

            # Update position based on the new angle
            x = a * np.cos(theta)
            z = b * np.sin(theta)
            y = 0  # You can adjust this if needed

            # Create the new transformation matrix
            model = glm.mat4(1.0)
            model = glm.translate(model, glm.vec3(x, y, z))  # Position in orbit
            scale_factor = self.scales[i]  # Use the stored scale factor
            model = glm.scale(model, glm.vec3(scale_factor, scale_factor, scale_factor))

            updated_matrices.append(np.array(model).T)

        # Update the instance buffer with the new matrices
        self.instance_buffer.write(np.array(updated_matrices, dtype='f4').tobytes())

    def render(self):
        """Renderització del VAO
        """
        self.texture.use()
        self.update_orbit()
        self.vao.render(instances=self.num_asteroids)

    def get_data(self):
        """Genera esfera (asteroides)"""
        return self.create_sphere(False)
