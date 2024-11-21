import glm
import numpy as np
import moderngl as mgl
from PIL import Image

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
    
    def get_model_matrix(self):
        """Obtenció de la model matrix
        Returns:
            glm.vec4: Matriu model 
        """
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        return m_model 
    
