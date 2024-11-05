import glm
import numpy as np
import moderngl as mgl
import os
from PIL import Image
import math

class Object:
    __slots__=["app",
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
               "radius"
               ]
    
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
    __slots__=["positions", "color"]
    
    """Classe filla d'Objecte. Crea les estrelles que envoltarà tot el Sistema Solar.
    """
    def __init__(self, app, shader, texture, info, positions):
        """Inicialització de la classe StarBatch

        Args:
            positions (glm.vec3): Posició en l'espai de l'estrella 
        """
        self.positions = positions
        self.color = glm.vec3(1.0, 1.0, 1.0)
        super().__init__(app, shader, texture, info)
    
    def on_init(self):
        """Post-inicialització de la classe StarBatch
        """
        # Essential for viewing
        self.shader['m_proj'].write(self.app.camera.m_proj)
        self.shader['m_view'].write(self.app.camera.m_view)
        self.shader['m_model'].write(self.m_model)
        self.shader['star_color'].write(self.color)

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
        data = np.array([(x, y, z) for x, z, y in self.positions], dtype='f4')
        return data
    
    def get_vao(self):
        """Obtenció del VAO
        """
        return self.ctx.vertex_array(self.shader, [(self.vbo, '3f', 'in_position')])
