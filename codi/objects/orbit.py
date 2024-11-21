import glm
import moderngl as mgl
import numpy as np
from objects.object import Object

class Orbit(Object):
    __slots__=["position", "eccentricity"]

    """Classe filla d'Objecte. Crea les òrbites dels planetes (traça el·lipses del seu moviment).
    """
    def __init__(self, app, shader, texture, info, position, eccentricity):
        """Inicialització de la classe Orbit

        Args:
            position (glm.vec3): Posició del planeta
            eccentricity (float): Excentritat de l'el·lipse
        """
        self.position = position
        self.eccentricity = eccentricity
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
        b = a * (1 - self.eccentricity ** 2) ** 0.5  # Semieix menor

        orbit_points = []

        for i in range(num_points):
            theta = 2 * np.pi * i / num_points  # Ángulo en radianes
            x = a * np.cos(theta)
            z = b * np.sin(theta)
            orbit_points.append((x, 0, z))

        return np.array(orbit_points, dtype='f4')
    