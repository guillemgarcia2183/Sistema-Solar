import numpy as np
import moderngl as mgl
from objects.object import Object
import glm
from PIL import Image

class RingBatch(Object):
    """Classe que crea els anells de Saturn, heretat de la classe Objecte
    """
    __slots__ = (
        "planet_distance",
        "ring_inner_radius",
        "ring_outer_radius",
        "velocity_planet",
        "eccentricity_planet",
        "num_segments",
        "num_instances",
        "radii",
        "instance_ids",
        "instance_buffer",
        "instance_id_buffer",
        "velocity_rings",
        "model_matrix_buffer"
        )
    def __init__(self, app, shader, texture, info, planet_distance, ring_inner_radius, ring_outer_radius, velocity, eccentricity, num_segments=500, num_instances=500):
        """Inicialització de la classe RingBatch

        Args:
            planet_distance (float): _description_
            ring_inner_radius (float): _description_
            ring_outer_radius (float): _description_
            velocity (float): _description_
            eccentricity (float): _description_
            num_segments (int, optional): _description_. Defaults to 500.
            num_instances (int, optional): _description_. Defaults to 500.
        """
        self.planet_distance = planet_distance
        self.ring_inner_radius = ring_inner_radius
        self.ring_outer_radius = ring_outer_radius
        self.velocity_planet = velocity
        self.eccentricity_planet = eccentricity
        self.num_segments = num_segments
        self.num_instances = num_instances
        super().__init__(app, shader, texture, info)
        # Generate instance-specific transformation matrices

    def on_init(self):
        """Post-inicialització de la classe
        """
        self.shader['m_model'].write(self.m_model)
        self.shader['m_view'].write(self.app.camera.m_view)
        self.shader['m_proj'].write(self.app.camera.m_proj)

    def get_data(self):
        """Obtenció de les dades dels anells 

        Returns:
            np.darray: Posicions dels vèrtex i coordenades textura
        """
        vertices = []
        for i in range(self.num_segments):
            angle = 2 * np.pi * i / self.num_segments
            next_angle = 2 * np.pi * (i + 1) / self.num_segments

            # Coordenadas en el círculo unitario
            x_start, z_start = np.cos(angle), np.sin(angle)
            x_end, z_end = np.cos(next_angle), np.sin(next_angle)

            # Coordenadas de textura
            tex_u = i / self.num_segments

            # Agregar los vértices
            vertices.extend([
                x_start, 0, z_start, tex_u, 0,  # Punto inicial
                x_end, 0, z_end, tex_u, 1,     # Punto final
            ])

        # Convertir los datos de vértices a un array de tipo 'f4' (float de 32 bits)
        return np.array(vertices, dtype='f4')
        
    def get_vao(self):
        """Obtenció del VAO
        """
        # Cálculo de los radios interpolados entre el radio interno y externo
        self.radii = np.linspace(self.ring_inner_radius, self.ring_outer_radius, self.num_instances).astype('f4')
        self.velocity_rings = np.linspace(self.velocity_planet, self.velocity_planet/100, self.num_instances).astype('f4')
        self.instance_ids = np.arange(self.num_instances, dtype='f4')
        # Crear un buffer para instancias
        self.model_matrix_buffer = self.ctx.buffer(reserve=self.num_instances * 64)
        self.instance_buffer = self.ctx.buffer(self.radii.tobytes())
        self.instance_id_buffer = self.ctx.buffer(self.instance_ids.tobytes())  # Buffer para identificadores de instancia

        # Actualizar el VAO para usar el buffer de instancias
        return self.ctx.vertex_array(self.shader,
            [(self.vbo, '3f 2f', 'in_position', 'in_texcoord'),
             (self.instance_buffer, '1f/i', 'instance_radius'),
             (self.instance_id_buffer, '1f/i', 'instance_id'),
             (self.model_matrix_buffer, '16f/i', 'model_matrix')]
        )

    def load_texture(self, filepath):
        """Carregar la textura d'entrada 

        Args:
            filepath (str): Path on està la imatge a texturitzar l'objecte

        Returns:
            mgl.texture: Textura
        """
        image = Image.open(filepath).transpose(Image.FLIP_TOP_BOTTOM)
        texture = self.ctx.texture(image.size, 4, image.tobytes())
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()
        texture.repeat_x = False
        texture.repeat_y = False
        return texture
    
    def move(self):
        """Actualitzar l'òrbita dels anells
        """
        self.rotate_sun()
        self.rotate_ring()
        
    def render(self):
        """Renderització del VAO
        """
        self.texture.use()
        self.vao.render(mgl.LINES, instances = self.num_instances)

    def rotate_sun(self):
        """Rotació dels anells respecte el Sol
        """
        m_model = glm.mat4()
        
        # Semieje mayor y menor basados en la distancia inicial del planeta al Sol
        a = glm.length(glm.vec2(self.planet_distance, self.planet_distance))  # La magnitud en XZ como semieje mayor
        b = a * (1 - self.eccentricity_planet ** 2) ** 0.5 # Semieje menor (ajústalo según el grado de excentricidad que desees)
        focal_distance = a * self.eccentricity_planet

        # Calcular el ángulo en función del tiempo
        theta = self.app.time * self.velocity_planet   # Ajusta la velocidad de la órbita

        # Posición del planeta en la órbita elíptica (plano XZ)
        x = a * glm.cos(theta) - focal_distance
        z = b * glm.sin(theta)

        # Trasladar el anillo a la posición de Saturno
        m_model = glm.translate(m_model, glm.vec3(x, 0, z))
        m_model = glm.rotate(m_model, glm.radians(27), glm.vec3(0, 0, 1))
        self.m_model = m_model
        self.shader['m_model'].write(self.m_model)

    def rotate_ring(self):
        """Rotació dels anells sobre ells mateixos
        """
        # Crear un array para almacenar las matrices de modelo de cada anillo
        model_matrices = np.zeros((self.num_instances, 16), dtype='f4')

        for i in range(self.num_instances):
            # Calcular el ángulo de rotación basado en el tiempo y la velocidad del anillo
            angle = self.app.time * self.velocity_rings[i]

            # Crear una matriz de rotación para este anillo
            rotation_matrix = glm.rotate(glm.mat4(), angle, glm.vec3(0, 1, 0))

            # Convertir la matriz glm a un array numpy y almacenarla
            model_matrices[i] = np.array(rotation_matrix).flatten()

        self.model_matrix_buffer.write(model_matrices.tobytes())