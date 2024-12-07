import unittest
import sys
import os
import glm

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from engine import GraphicsEngine
import shaders as sh
from objects import *

class TestSatellites(unittest.TestCase):
    __slots__ = ('object')
    def setUp(self):
        """Crea una instància de Satellite
        """
        # Initialize a Satellite object before each test
        self.object = Satellite(GraphicsEngine(testing=True),
                       [sh.vertex_shader_SUN, sh.fragment_shader_SUN],
                       "textures/earth.jpg",
                       [1.0,10,10],
                       glm.vec3(1, 1, 1),
                       glm.vec3(15,15,15),
                       glm.vec3(20, 20, 20),
                       10.0,
                       5.0,
                       10.0,
                       0.05,
                       )
    
    def test_initialization(self):
        """1. Test d'inicialització de la classe
        """
        # Test if the Satellite is initialized with no problems
        self.assertIsInstance(self.object, Satellite)
        self.assertIsInstance(self.object.size, glm.vec3)
        self.assertIsInstance(self.object.position_planet, glm.vec3)
        self.assertIsInstance(self.object.position_satellite, glm.vec3)
        self.assertIsInstance(self.object.velocity_planet, float)
        self.assertIsInstance(self.object.velocity_satellite, float)
        self.assertIsInstance(self.object.inclination, float)
        self.assertIsInstance(self.object.eccentricity, float)

    def test_rotation(self):
        """2. Test de rotació dels planetes
        """
        # Test if the Satellite rotates correctly
        original_m_model = self.object.m_model
        position = self.object.rotate_sun()
        self.object.rotate_planet(position)
        self.object.rotate_self()
        self.assertNotEqual(self.object.m_model, original_m_model)

if __name__ == '__main__':
    unittest.main()
