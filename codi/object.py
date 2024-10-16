import glm
import numpy as np

class Object:
    def __init__(self, app, shader, info = ["octahedron", 3]):
        self.app = app
        self.ctx = app.ctx

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

    def get_vbo(self):
        data = self.get_data()
        vbo = self.ctx.buffer(data)
        return vbo
    
    def destroy(self):
        self.vbo.release()
        self.faces_shader.release()
        self.vao.release()    

    def get_vao(self):
        vao = self.ctx.vertex_array(self.faces_shader,[(self.vbo, '3f 3f 3f', 'in_color', 'in_norm', 'in_position')])
        return vao

    def get_octahedron(self):
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
 
        # Octahedron faces (triangles)
        faces = [(0,4,1), (0,3,4), (0,1,5), (0,5,3), (2,4,3), (2,1,4), (2,3,5), (2,5,1)]

        return vertices, faces

    def subdivide_faces(self, vertices, faces):
        new_faces = []
        midpoint_cache = {}

        def get_midpoint(v1_idx, v2_idx):
            """ Return the midpoint between two vertices, caching the result to avoid duplicates. """
            smaller_idx = min(v1_idx, v2_idx)
            larger_idx = max(v1_idx, v2_idx)
            key = (smaller_idx, larger_idx)

            if key in midpoint_cache:
                return midpoint_cache[key]

            v1 = vertices[v1_idx]
            v2 = vertices[v2_idx]
            midpoint = (v1 + v2) / 2.0

            # Normalize the midpoint to lie on the unit sphere
            midpoint = self.normalize(midpoint)

            # Add the new vertex and return its index
            midpoint_idx = len(vertices)
            vertices.append(midpoint)
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
        norm = np.linalg.norm(v)
        return v / norm

    def get_faces_shader_program(self, shader):
        program = self.ctx.program(vertex_shader= shader[0], fragment_shader= shader[1])
        return program
    
class Sun(Object): # EL SOL TÉ LES NORMALS EN NEGATIU, DE MOMENT ÉS L'ÚNIC CANVI RESPECTE LES ALTRES ESFERES
    def get_model_matrix(self):
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        return m_model

    def render(self):
        self.vao.render()

    def get_data(self):
        color = glm.vec3(1, 1, 0)
        data = []
        if self.method == "stripes":
            vertices = []
            indices = []
            # Latitude and longitude angles in radians
            for lat in range(self.lat + 1):
                theta = np.pi * lat / self.lat
                for lon in range(self.lon):
                    phi = 2 * np.pi * lon / self.lon
                    # Spherical to Cartesian conversion
                    x = self.radius * np.sin(theta) * np.cos(phi)
                    y = self.radius * np.cos(theta)
                    z = self.radius * np.sin(theta) * np.sin(phi)
                    vertices.append((x, y, z))

            # Create faces (triangles) between vertices (latitude-longitude stripes)
            for lat in range(self.lat):
                for lon in range(self.lon):
                    current = lat * self.lon + lon
                    next = current + self.lon
                    indices.append((current, next, current + 1))
                    indices.append((current + 1, next, next + 1))

            for face in indices:
                for idx in face:
                    vertex = glm.vec3(vertices[idx-1])
                    normalized_v = self.normalize(vertex)
                    data.extend([color.x, color.y, color.z]) # in_color
                    data.extend([-normalized_v.x, -normalized_v.y, -normalized_v.z]) # in_norm
                    data.extend([vertex.x, vertex.y, vertex.z]) # in_position

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

                    data.extend([color.x, color.y, color.z]) # in_color
                    data.extend([-normalized_v.x, -normalized_v.y, -normalized_v.z]) # in_norm
                    data.extend([vertex.x, vertex.y, vertex.z]) # in_position

        return np.array(data, dtype='f4')

class Planet(Object):
    def __init__(self, app, shader, info, color, size, position):
        # Característiques de l'esfera
        self.color = color
        self.size = size
        self.position = position
        super().__init__(app, shader, info)

    def get_model_matrix(self):
        m_model = glm.rotate(glm.mat4(), glm.radians(0), glm.vec3(0, 1, 0))
        m_model = glm.scale(m_model, self.size)  
        m_model = glm.translate(m_model, self.position)   
        return m_model
    
    def render(self):
        self.vao.render()
    
    def get_data(self):
        data = []
        if self.method == "stripes":
            vertices = []
            indices = []
            # Latitude and longitude angles in radians
            for lat in range(self.lat + 1):
                theta = np.pi * lat / self.lat
                for lon in range(self.lon):
                    phi = 2 * np.pi * lon / self.lon
                    # Spherical to Cartesian conversion
                    x = self.radius * np.sin(theta) * np.cos(phi)
                    y = self.radius * np.cos(theta)
                    z = self.radius * np.sin(theta) * np.sin(phi)
                    vertices.append((x, y, z))

            # Create faces (triangles) between vertices (latitude-longitude stripes)
            for lat in range(self.lat):
                for lon in range(self.lon):
                    current = lat * self.lon + lon
                    next = current + self.lon
                    indices.append((current, next, current + 1))
                    indices.append((current + 1, next, next + 1))

            for face in indices:
                for idx in face:
                    vertex = glm.vec3(vertices[idx-1])
                    normalized_v = self.normalize(vertex)
                    data.extend([self.color.x, self.color.y, self.color.z]) # in_color
                    data.extend([normalized_v.x, normalized_v.y, normalized_v.z]) # in_norm
                    data.extend([vertex.x, vertex.y, vertex.z]) # in_position

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

                    data.extend([self.color.x, self.color.y, self.color.z]) # in_color
                    data.extend([normalized_v.x, normalized_v.y, normalized_v.z]) # in_norm
                    data.extend([vertex.x, vertex.y, vertex.z]) # in_position

        return np.array(data, dtype='f4')

