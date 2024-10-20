import glm

class Light:
    """Classe per establir l'il·luminació dels objectes
    """
    def __init__(self, position=(0,0,0), color=(1,1,1)):
        """Inicialització de la classe Light

        Args:
            position (tuple, optional): Vector de la posició on estarà el focus de llum. Defaults to (0,0,0).
            color (tuple, optional): Vector del color de la llum. Defaults to (1,1,1).
        """
        self.position = glm.vec3(position)
        self.color = glm.vec3(color)
        # intensities
        self.Ia = 0.1 * self.color # ambient
        self.Id = 0.8 * self.color # diffuse
        self.Is = 1.0 * self.color # specular 