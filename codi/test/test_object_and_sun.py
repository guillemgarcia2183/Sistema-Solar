import unittest
import sys
import os
import moderngl as mgl
import glm

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from engine import GraphicsEngine
import shaders as sh
from objects import *

class TestObject(unittest.TestCase):
    __slots__ = ('object')
    def setUp(self):
        """Crea una instància de Sun
        """
        # Initialize a Sun object before each test
        self.object = Sun(GraphicsEngine(testing=True),
                       [sh.vertex_shader_SUN, sh.fragment_shader_SUN],
                       "textures/sun.jpg",
                       [1.0,10,10])

    def test_initialization(self):
        """1. Test d'inicialització de la classe
        """
        # Test if the Sun is initialized with no problems
        self.assertIsInstance(self.object, Sun)
        self.assertIsInstance(self.object.app, GraphicsEngine)
        self.assertIsInstance(self.object.radius, float)
        self.assertIsInstance(self.object.lat, int)
        self.assertIsInstance(self.object.lon, int)
        self.assertIsInstance(self.object.texture, mgl.Texture)
        self.assertIsInstance(self.object.shader, mgl.Program)
        self.assertIsInstance(self.object.vbo, mgl.Buffer)
        self.assertIsInstance(self.object.vao, mgl.VertexArray)
        self.assertIsInstance(self.object.m_model, glm.mat4x4)

    def test_sphere_creation(self):
        """2. Test de la creació de les esferes
        """
        sphere = self.object.create_sphere(False)
        self.assertEqual(len(sphere), 4800)
        self.assertGreaterEqual(sphere[6], 0)
        self.assertLessEqual(sphere[6], 1)
        self.assertGreaterEqual(sphere[7], 0)
        self.assertLessEqual(sphere[7], 1)

if __name__ == '__main__':
    unittest.main()
