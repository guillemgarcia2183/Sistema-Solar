import glm
import math
from objects.object import Object

class Satellite(Object):
    __slots__=["size", "position_planet", "position_satellite", "velocity_planet", "velocity_satellite", "inclination", "eccentricity"]
    
    """Classe filla d'Objecte. Crea els Satèl·lits naturals.
    """
    def __init__(self, app, shader, texture, info, size, position_planet, position_satellite, velocity_planet, velocity_satellite, inclination, eccentricity):
        """Inicialització de la classe Planet. Tindrà els atributs de Object i els següents

        Args:
            size (glm.vec3): Mida del satèl·lit
            position_planet (glm.vec3): Posició del planeta 
            position_satellite (glm.vec3): Posició del satèl·lit
            velocity_planet (float): Velocitat del planeta
            velocity_satellite (float): Velocitat del satèl·lit
            inclination (float): Inclinació de rotació
            eccentricity (float): Excentritat de l'el·lipse
        """
        # Característiques de l'esfera
        self.size = size
        self.position_planet = position_planet
        self.position_satellite = position_satellite
        self.velocity_planet = velocity_planet
        self.velocity_satellite = velocity_satellite
        self.inclination = inclination
        self.eccentricity = eccentricity
        super().__init__(app, shader, texture, info)
        
    def get_model_matrix(self):
        """Obtenció de la model matrix
        Returns:
            glm.vec4: Matriu model 
        """
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        m_model = glm.scale(m_model, self.size)  
        m_model = glm.translate(m_model, self.position_satellite)   
        return m_model
            
    def get_data(self):
        return self.create_sphere(False)
    
    def move(self):
        planet_position = self.rotate_sun()
        self.rotate_planet(planet_position)
        self.rotate_self()

    def render(self):
        """Renderització del VAO i rotació dels planetes
        """
        self.texture.use()
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
        distance = self.position_satellite - self.position_planet
        a = glm.length(glm.vec2(distance.x, distance.z))
        b = a * (1 - self.eccentricity ** 2) ** 0.5  # Excentricidad de la órbita del satélite
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
        a = glm.length(glm.vec2(self.position_planet.x, self.position_planet.z))
        b = a * (1 - self.eccentricity ** 2) ** 0.5
        theta = self.app.time * self.velocity_planet

        # Calcular la posición en la órbita elíptica (eje XZ) respecto al Sol
        x = a * glm.cos(theta)
        z = b * glm.sin(theta)
        y = self.position_planet.y

        # Posición de la órbita alrededor del Sol
        planet_position = glm.vec3(x, y, z)
        
        return planet_position  # Devolver la posición del planeta
