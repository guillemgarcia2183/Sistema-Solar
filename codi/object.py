import glm
import numpy as np
import moderngl as mgl
import os
from PIL import Image
import math

class Object:
    """Classe per crear un objecte dintre del Sistema Solar (classe pare)
    """
    def __init__(self, app, shader, texture, info = ["octahedron", 3]):
        """Inicialització de la classe Object

        Args:
            app (GraphicsEngine()): Instància de la classe GraphicsEngine()
            shader (list): Llista que conté el vertex_shader i fragment_shader a utilitzar 
            info (list, optional): Informació per crear les esferes (en cas de planetes i sol). Defaults to ["octahedron", 3].
        """
        self.app = app
        self.ctx = app.ctx
        self.texture = self.load_texture(texture)

        self.method = info[0]
        if self.method == "stripes":
            self.radius = info[1]
            self.lat = info[2]
            self.lon = info[3]
        
        elif self.method == "octahedron": 
            self.subdivisions = info[1]

        self.vbo = self.get_vbo()
        self.faces_shader = self.get_faces_shader_program(shader)
        self.vao = self.get_vao()

        self.m_model = self.get_model_matrix()
        self.on_init()

    def on_init(self):
        """Pos-inicialització de la classe Object. Establiment dels paràmetres del shader 
        """
        # Related to lighting
        self.faces_shader['light.position'].write(self.app.light.position)
        self.faces_shader['view_pos'].write(self.app.camera.position)
        self.faces_shader['light.Ia'].write(self.app.light.Ia)
        self.faces_shader['light.Id'].write(self.app.light.Id)
        self.faces_shader['light.Is'].write(self.app.light.Is)

        # Essential for viewing
        self.faces_shader['m_proj'].write(self.app.camera.m_proj)
        self.faces_shader['m_view'].write(self.app.camera.m_view)
        self.faces_shader['m_model'].write(self.m_model)

    def load_texture(self, filepath):
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
        self.faces_shader.release()
        self.texture.release()
        self.vao.release()    

    def get_vao(self):
        """Obtenció del VAO 

        Returns:
            moderngl.VertexArray: Array VAO
        """
        #vao = self.ctx.vertex_array(self.faces_shader,[(self.vbo, '3f 3f 3f 2f', 'in_color', 'in_norm', 'in_position', 'in_tex_coord')])
        vao = self.ctx.vertex_array(self.faces_shader,[(self.vbo, '3f 3f 2f', 'in_norm', 'in_position', 'in_tex_coord')])
        return vao

    def get_octahedron(self):
        """Creació d'un octaedre (per tal de fer l'esfera per subdivisió)

        Returns:
            (list, list): Vèrtexs i arestes del octaedre
        """
        # Create vertices of an octahedron
        v1 = np.array([0.,0.,0.])
        v2 = np.array([1.,0.,0.])
        v3 = np.array([1.,0.,1.])
        v4 = np.array([0.,0.,1.])
        v5 = np.array([0.5,1.,0.5])
        v6 = np.array([0.5,-1.,0.5])
        c = (v1+v2+v3+v4+v5+v6)/6.0  # calculo el centre per treure'l i centrar la figura
        v1-=c
        v2-=c
        v3-=c
        v4-=c
        v5-=c
        v6-=c
        vertices = [v1, v2, v3, v4, v5, v6]

        for i in range(len(vertices)):
            n_v = self.normalize(vertices[i])
            s = (0.5 + (np.arctan2(n_v[2], n_v[0]) / (2 * np.pi))) % 1.0
            t = 0.5 - (np.arcsin(n_v[1]) / np.pi)
            vertices[i] = [vertices[i], s,t]

        # Octahedron faces (triangles)
        faces = [(0,4,1), (0,3,4), (0,1,5), (0,5,3), (2,4,3), (2,1,4), (2,3,5), (2,5,1)]

        return vertices, faces

    def subdivide_faces(self, vertices, faces):
        """Mètode de subdivisió 

        Args:
            vertices (list): Vèrtexs octaedre
            faces (list): Arestes octaedre

        Returns:
            list: Arestes actualitzades
        """
        new_faces = []
        midpoint_cache = {}

        def get_midpoint(v1_idx, v2_idx):
            """ Return the midpoint between two vertices, caching the result to avoid duplicates. """
            smaller_idx = min(v1_idx, v2_idx)
            larger_idx = max(v1_idx, v2_idx)
            key = (smaller_idx, larger_idx)

            if key in midpoint_cache:
                return midpoint_cache[key]

            v1 = vertices[v1_idx][0]
            v2 = vertices[v2_idx][0]
            midpoint = (v1 + v2) / 2.0

            # Normalize the midpoint to lie on the unit sphere
            midpoint = self.normalize(midpoint)
            s = (0.5 + (np.arctan2(midpoint[2], midpoint[0]) / (2 * np.pi))) % 1.0
            t = 0.5 - (np.arcsin(midpoint[1]) / np.pi)

            # Add the new vertex and return its index
            midpoint_idx = len(vertices)
            vertices.append([midpoint, s, t])
            midpoint_cache[key] = midpoint_idx
            return midpoint_idx

        # Subdivide each face
        for v1, v2, v3 in faces:
            # Calculate midpoints
            m1 = get_midpoint(v1, v2)
            m2 = get_midpoint(v2, v3)
            m3 = get_midpoint(v3, v1)

            # Create 4 new faces
            new_faces.extend([
                (v1, m1, m3),
                (v2, m2, m1),
                (v3, m3, m2),
                (m1, m2, m3)
            ])

        return new_faces

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

    def get_faces_shader_program(self, shader):
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
        """
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
        """Funció per obtenir l'esfera (coordenades esfèriques / subdivisió)

        Returns:
            np.array: Dades per renderitzar l'esfera (color, normal, position)
        """
        #color = glm.vec3(1, 1, 0)
        data = []
        if self.method == "stripes":
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
                    #data.extend([color.x, color.y, color.z])  # in_color
                    data.extend([-normalized_v.x, -normalized_v.y, -normalized_v.z])  # in_norm
                    data.extend([vertex.x, vertex.y, vertex.z])  # in_position
                    data.extend([s, t])  # in_tex_coord

        elif self.method == "octahedron":
            # Generate the octahedron and subdivide it into a sphere
            octahedron_vertices, octahedron_faces = self.get_octahedron()

            # Subdivide the octahedron faces to form the sphere
            for _ in range(self.subdivisions):
                octahedron_faces = self.subdivide_faces(octahedron_vertices, octahedron_faces)

            # Normalize all vertices to project them onto a unit sphere
            for i in range(len(octahedron_vertices)):
                octahedron_vertices[i][0] = self.normalize(octahedron_vertices[i][0])

            for face in octahedron_faces:
                for idx in face:
                    v, s, t = octahedron_vertices[idx]
                    vertex =  glm.vec3(v)
                    normalized_v = self.normalize(vertex)

                    #data.extend([color.x, color.y, color.z]) # in_color
                    data.extend([-normalized_v.x, -normalized_v.y, -normalized_v.z]) # in_norm
                    data.extend([vertex.x, vertex.y, vertex.z]) # in_position
                    
                    data.extend([s,t]) # in_tex_coord

        return np.array(data, dtype='f4')

class Planet(Object):
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
        """
        Returns:
            glm.vec4: Matriu model 
        """
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        m_model = glm.scale(m_model, self.size)  
        m_model = glm.translate(m_model, self.position)   
        return m_model
            
    def get_data(self):
        """Funció per obtenir l'esfera (coordenades esfèriques / subdivisió)

        Returns:
            np.array: Dades per renderitzar l'esfera (color, normal, position)
        """
        data = []
        if self.method == "stripes":
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
                    data.extend([normalized_v.x, normalized_v.y, normalized_v.z])  # in_norm
                    data.extend([vertex.x, vertex.y, vertex.z])  # in_position
                    data.extend([s, t])  # Texture coordinates

        elif self.method == "octahedron":
            # Generate the octahedron and subdivide it into a sphere
            octahedron_vertices, octahedron_faces = self.get_octahedron()

            # Subdivide the octahedron faces to form the sphere
            for _ in range(self.subdivisions):
                octahedron_faces = self.subdivide_faces(octahedron_vertices, octahedron_faces)

            # Normalize all vertices to project them onto a unit sphere
            for i in range(len(octahedron_vertices)):
                octahedron_vertices[i] = self.normalize(octahedron_vertices[i])

            for face in octahedron_faces:
                for idx in face:
                    vertex = glm.vec3(octahedron_vertices[idx])
                    normalized_v = self.normalize(vertex)

                    #data.extend([self.color.x, self.color.y, self.color.z]) # in_color
                    data.extend([normalized_v.x, normalized_v.y, normalized_v.z]) # in_norm
                    data.extend([vertex.x, vertex.y, vertex.z]) # in_position

        return np.array(data, dtype='f4')
    
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
        self.faces_shader['m_model'].write(self.m_model)
        
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
    def __init__(self, app, shader, texture, info, position, excentrity):
        self.position = position
        self.excentrity = excentrity
        super().__init__(app, shader, texture, info)

    def on_init(self):
        # Essential for viewing
        self.faces_shader['m_proj'].write(self.app.camera.m_proj)
        self.faces_shader['m_view'].write(self.app.camera.m_view)
        self.faces_shader['m_model'].write(self.m_model)
        orbit_color = glm.vec3(1.0, 1.0, 1.0)  # RGB blanco
        self.faces_shader['orbit_color'].write(orbit_color)

    def get_vao(self):
        return self.ctx.vertex_array(self.faces_shader, [(self.vbo, '3f', 'in_position')])
    
    def get_model_matrix(self):
        """
        Returns:
            glm.vec4: Matriu model 
        """
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        return m_model

    def update(self):
        self.faces_shader['m_view'].write(self.app.camera.m_view)

    def render(self):
        """Renderització del VAO
        """
        self.update()
        self.vao.render(mgl.LINE_LOOP) 


    def get_data(self, num_points = 200):
        """Genera los puntos de la órbita del planeta alrededor del sol.
    
        Args:
            num_points (int): Número de puntos que describen la órbita.
        
        Returns:
            np.array: Array con los puntos en la órbita.
        """
        # Parámetros de la órbita
        a = glm.length(glm.vec2(self.position.x, self.position.z))  # Semieje mayor
        b = a * (1 - self.excentrity ** 2) ** 0.5  # Semieje menor

        orbit_points = []

        for i in range(num_points):
            theta = 2 * np.pi * i / num_points  # Ángulo en radianes
            x = a * np.cos(theta)
            z = b * np.sin(theta)
            orbit_points.append((x, 0, z))

        return np.array(orbit_points, dtype='f4')
    
class StarBatch(Object):
    def __init__(self, app, shader, texture, info, positions):
        self.positions = positions
        self.color = glm.vec3(1.0, 1.0, 1.0)
        super().__init__(app, shader, texture, info)
    
    def on_init(self):
        # Essential for viewing
        self.faces_shader['m_proj'].write(self.app.camera.m_proj)
        self.faces_shader['m_view'].write(self.app.camera.m_view)
        self.faces_shader['m_model'].write(self.m_model)
        self.faces_shader['star_color'].write(self.color)

    def get_model_matrix(self):
        # NOTE: Order of operations is from last -> first

        # in-world placement of the star
        rads = glm.radians(23.44)
        #m_model *= glm.translate(self.position) #TODO: Is this correct?
        m_model = glm.translate(-self.app.objects[1].position)
        m_model *= glm.rotate(glm.mat4(), rads, glm.vec3(0, 0, 1))

        return m_model
    
    def update(self):
        self.faces_shader['m_view'].write(self.app.camera.m_view)

    def render(self):
        self.update()
        self.ctx.enable(mgl.PROGRAM_POINT_SIZE)
        self.ctx.point_size = 3
        self.vao.render(mgl.POINTS)

    def get_data(self):
        #data = np.array([self.position.x, self.position.y, self.position.z], dtype='f4')
        data = np.array([(x, y, z) for x, z, y in self.positions], dtype='f4')
        return data
    
    def get_vao(self):
        return self.ctx.vertex_array(self.faces_shader, [(self.vbo, '3f', 'in_position')])
