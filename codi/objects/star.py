import glm
import moderngl as mgl
import numpy as np
from objects.object import Object

class StarBatch(Object):
    __slots__ = (
        "positions",
        "constellations",
        "constellations_shader",
        "constellations_vao"
    )
    
    """Classe filla d'Objecte. Crea les estrelles que envoltarà tot el Sistema Solar.
    """
    def __init__(self, app, shader, texture, info, positions, constellations=True, **kwargs):

        """Inicialització de la classe StarBatch

        Args:
            positions (glm.vec3): Posició en l'espai de l'estrella 
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
        m_model = glm.translate(-self.app.objects[1].position)
        m_model *= glm.rotate(glm.mat4(), rads, glm.vec3(0, 0, 1))

        return m_model
    
    def update(self):
        """Actualització de la càmera al moure-la
        """
        self.shader['m_view'].write(self.app.camera.m_view)
        self.constellations_shader['m_view'].write(self.app.camera.m_view)

    def render(self):
        """Renderització de l'estrella
        """
        self.update()
        self.ctx.enable(mgl.PROGRAM_POINT_SIZE)
        self.ctx.point_size = 3
        self.vao.render(mgl.POINTS)

        if self.constellations:
            self.constellations_vao.render(mgl.LINES)

    def get_constellations_vao(self):
        """ This function creates an index buffer object that points to the stars
            that have a common constellation.
            Enif -- Biham
            Biham -- Homam
            Homam -- Markab
            Markab -- Algenib
            Markab -- Scheat

        """
        
        if (not self.constellations):
            return None

        star_indices = dict()
        index = 0
        for _, _, _, _, con, proper in self.positions:
            if (con == "Peg"):
                if isinstance(proper, str):
                    star_indices[proper] = index
            if (isinstance(proper, str) and proper== "Alpheratz"):
                    star_indices[proper] = index
            index += 1
            
        constellation_indices = [
            star_indices["Enif"],   star_indices["Biham"],
            star_indices["Biham"],  star_indices["Homam"],
            star_indices["Homam"],  star_indices["Markab"],
            star_indices["Markab"], star_indices["Algenib"],
            star_indices["Markab"], star_indices["Scheat"],
            star_indices["Scheat"], star_indices["Alpheratz"],
            star_indices["Algenib"], star_indices["Alpheratz"]
        ]

        ibo = self.ctx.buffer(np.array(constellation_indices, dtype='i4').tobytes())
        # perform an offset of self.ibo of 3*sizeof(float)
        # and a stride of 24 = 6*sizeof(float) according to the format -> color vec3f and pos vec3f

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
