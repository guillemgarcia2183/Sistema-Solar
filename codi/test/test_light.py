import unittest
import sys
import os
import glm

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from light import Light

class TestLight(unittest.TestCase):
    __slots__ = ('light')
    def setUp(self):
        """Crea una instància de Light
        """
        # Initialize a Light object before each test
        self.light = Light()

    def test_initialization(self):
        """1. Test d'inicialització de la classe
        """
        # Test if the Light is initialized with no problems
        self.assertIsInstance(self.light, Light)
        self.assertIsInstance(self.light.position, glm.vec3)
        self.assertIsInstance(self.light.color, glm.vec3)
        self.assertIsInstance(self.light.Ia, glm.vec3)
        self.assertIsInstance(self.light.Id, glm.vec3)
        self.assertIsInstance(self.light.Is, glm.vec3)

if __name__ == '__main__':
    unittest.main()
