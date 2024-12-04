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

class TestPlanet(unittest.TestCase):
    __slots__ = ('object')
    def setUp(self):
        """Crea una instància de Planet
        """
        # Initialize a Planet object before each test
        self.object = Planet(GraphicsEngine(testing=True),
                       [sh.vertex_shader_SUN, sh.fragment_shader_SUN],
                       "textures/earth.jpg",
                       [1.0,10,10],
                       glm.vec3(15, 1, 15),
                       glm.vec3(20, 1, 20),
                       10.0,
                       10.0,
                       0.05,
                       )
    

    def test_initialization(self):
        """1. Test d'inicialització de la classe
        """
        # Test if the Planet is initialized with no problems
        self.assertIsInstance(self.object, Planet)
        self.assertIsInstance(self.object.size, glm.vec3)
        self.assertIsInstance(self.object.original_pos, glm.vec3)
        self.assertIsInstance(self.object.velocity, float)
        self.assertIsInstance(self.object.inclination, float)
        self.assertIsInstance(self.object.eccentricity, float)

    def test_rotation(self):
        """2. Test de rotació dels planetes
        """
        # Test if the Planet rotates correctly
        original_m_model = self.object.m_model
        self.object.rotate_sun()
        self.object.rotate_self()
        self.assertNotEqual(self.object.m_model, original_m_model)
        
if __name__ == '__main__':
    unittest.main()
