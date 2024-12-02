from objects.object import Object

class Sun(Object): 
    """Classe filla d'Objecte. Crea el Sol. Es caracteritza per tenir les normals invertides de signe (per termes d'il·luminació)
    """
    def render(self):
        """Renderització del VAO
        """
        self.texture.use()
        self.vao.render()

    def get_data(self):
        """Obtenció de les dades que generen el sol 

        Returns:
            np.darray: Posicions dels vèrtexs i coordenades textures
        """
        return self.create_sphere(True)