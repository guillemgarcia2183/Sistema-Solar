import glm
import moderngl as mgl
import numpy as np

from objects.object import Object

class StarBatch(Object):
    """Classe filla d'Objecte. Crea les estrelles que envoltarà tot el Sistema Solar.
    """
    __slots__ = (
        "positions",
        "constellations",
        "constellations_shader",
        "constellations_vao",
    )
    def __init__(self, app, shader, texture, info, positions, constellations=True, **kwargs):

        """Inicialització de la classe StarBatch

        Args:
            positions (glm.vec3): Posició en l'espai de l'estrella
            constellations (bool): Indica si es vol mostrar les constellacions
            kwargs (dict): Paràmetres per inicialitzar la classe StarBatch 
        """
        self.positions = positions
        self.constellations = constellations
        self.constellations_shader = None
        self.constellations_vao = None
        super().__init__(app, shader, texture, info)
        
        if self.constellations:
            assert "constellations_shaders" in kwargs.keys(), "ERROR: No argument provided for shaders constellation"
            assert isinstance(kwargs["constellations_shaders"], list), \
                "ERROR: Bad argument format provided for shaders constellation correct is List[vertex: str, fragment: str]"
            assert len(kwargs["constellations_shaders"]) == 2, "ERRORt: too many/few arguments is shaders list"
        
        self.constellations_shader = self.ctx.program(
            kwargs["constellations_shaders"][0], #vertex_shader
            kwargs["constellations_shaders"][1], #fragment_shader
        )

        assert self.constellations_shader , "FATAL ERROR"

        self.on_init_2()

        self.constellations_vao = self.get_constellations_vao()
    
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

    def load_texture(self, filepath="textures/constellation_lines.png"):
        from PIL import Image
        with Image.open("textures/constellation_lines.png", 'r') as fTex:
            tex = self.ctx.texture([fTex.width, fTex.height], 4, np.array(fTex))
            #tex.filter = (mgl.GL_TEXTURE_MAG_FILTER, mgl.LINEAR)
            tex.repeat_x = True
            return tex

    def on_init_2(self):
        """Post-Post-inicialització de la classe StarBatch
        """
        self.constellations_shader['m_proj'].write(self.app.camera.m_proj)
        self.constellations_shader['m_view'].write(self.app.camera.m_view)
        self.constellations_shader['m_model'].write(self.m_model)
    
    def get_color_from_mag(self, mag):
        """Calcular el color que s'ha de pintar una estrella

        Args:
            mag (float): Magnitut de l'estrella

        Returns:
            glm.vec3: Color de l'estrella
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
        m_model = glm.translate(-self.app.objects[1].original_pos)
        m_model *= glm.rotate(glm.mat4(), rads, glm.vec3(0, 0, 1))

        return m_model
    
    def render(self):
        """Renderització de l'estrella
        """
        self.ctx.enable(mgl.PROGRAM_POINT_SIZE)
        self.ctx.point_size = 3
        self.vao.render(mgl.POINTS)

        if self.constellations:
            self.texture.use()
            self.constellations_vao.render(mgl.TRIANGLES)

    def get_constellations_vao(self):
        """ 
        Crea un nou vao que conté les estrelles que formen constelacions
        """
        if (not self.constellations):
            return None

        data = list()
        star_coords = dict()
        # Per millorar la visualització es projectaran les constelacion a la esfera de radi 750
        for x, y, z, _, _, proper in self.positions:
            if isinstance(proper, str):
                star_coords[proper] = 1000*glm.normalize(glm.vec3(x, y, z))
        
        consts = self.parse_constellations()
        
        tex_coords = [
            (0, 1),
            (0, 0),
            (1, 1),
            (1, 0)
        ]
        vertices = list()
        for v in consts.values():
            for pair in v:
                points = [star_coords[pair[0]], star_coords[pair[1]]]

                line_vector = points[1] - points[0]
                camera_vector = self.app.camera.position - points[0]
                delta = 5*glm.normalize(
                    glm.cross(
                        glm.normalize(line_vector),
                        glm.normalize(camera_vector)
                    )
                )

                for i in range(2):
                    p = points[i]
                    px = list(p+delta)
                    py = list(p-delta)
                    vertices.append(tuple([*px, *tex_coords[2*i]]))
                    vertices.append(tuple([*py, *tex_coords[2*i+1]]))

        indices = list()
        for i in range(0, len(vertices), 4):
            indices.append((i,   i+1, i+2))
            indices.append((i+2, i+3, i+1))
        
        consts_vbo = self.ctx.buffer(np.array([vertices[i] for idx in indices for i in idx], dtype='f4').tobytes())

        return self.ctx.vertex_array(
            self.constellations_shader,
            [(consts_vbo, '3f 2f', 'in_position', 'in_texcoords')]
        )

    def get_data(self):
        """Obtenció de les dades per generar el VBO

        Returns:
            np.array: Coordenades de les estrelles (position)
        """
        data = list()
        for x, z, y, mag, _, _ in self.positions:
            color = self.get_color_from_mag(mag)
            data.append((color.x, color.y, color.z,
                         x, y, z))
        data = np.array(data, dtype='f4')
        return data

    def parse_constellations(self, constellations_path: str = r"./data/constellations.txt"):
        """Crea les constel·lacions 

        Args:
            constellations_path (str, optional): Path del fitxer que conté les connexió de constel·lacions. Defaults to r"./data/constellations.txt".

        Returns:
            dict: Diccionari amb les constel·lacions
        """
        constellations = dict()
        with open(constellations_path, 'r') as fCo:
            current_const = None
            for line in fCo:
                if (not line):
                    continue

                if ('{' in line):
                    current_const = line.split()[0]
                    constellations[current_const] = list()
                elif (line.find('};') > 0):
                    current_const = None
                elif (line.find('};') < 0):
                    constellations[current_const].append(
                        tuple(part.strip() for part in line.strip().rstrip(" ").strip('\n').split('--'))
                    )

        return constellations
