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
        "constellations_vao"
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
            default_line_width = self.ctx.line_width
            self.ctx.line_width = 2.0
            self.constellations_vao.render(mgl.LINES)
            self.ctx.line_width = default_line_width 

    def get_constellations_vao(self):
        """ 
        Crea un index buffer que apunta a les estrelles que tenen una constel·lació en comú.
        """
        if (not self.constellations):
            return None

        star_indices = dict()
        index = 0
        for _, _, _, _, con, proper in self.positions:
            if isinstance(proper, str):
                star_indices[proper] = index
            index += 1

        consts = self.parse_constellations()
        constellation_indices = list()

        #print(consts)

        for v in consts.values():
            for pair in v:
                constellation_indices.append(star_indices[pair[0]]) 
                constellation_indices.append(star_indices[pair[1]])


        ibo = self.ctx.buffer(np.array(constellation_indices, dtype='i4').tobytes())

        # TODO: We don't need color here but it doesn't work without it 
        return self.ctx.vertex_array(
            self.constellations_shader,
            [(self.vbo, '3f 3f', 'in_color', 'in_position')], 
            index_buffer=ibo
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
