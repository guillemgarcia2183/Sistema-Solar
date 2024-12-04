import unittest
import sys
import os
import glm

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from engine import GraphicsEngine
from reader import Reader
import shaders as sh
from objects import *

class TestStar(unittest.TestCase):
    __slots__ = ('object')
    def setUp(self):
        """Crea una instància de StarBatch
        """
        star_reader = Reader.read_stars("data/stars.csv")
        self.object = star_reader.make_stars(
                                    StarBatch,
                                    GraphicsEngine(testing=True),
                                    [sh.vertex_shader_STAR, sh.fragment_shader_STAR],
                                    "textures/earth.jpg",  # Won't put a texture
                                    [0, 0, 0],
                                    constellations=True,
                                    constellations_shaders=[sh.vertex_shader_CONSTELLATION, sh.fragment_shader_CONSTELLATION]
                                )

    def test_initialization(self):
        """1. Test d'inicialització de la classe
        """
        # Test if the StarBatch is initialized with no problems
        self.assertIsInstance(self.object, StarBatch)
        self.assertIsInstance(self.object.positions, Reader)
        self.assertIsInstance(self.object.constellations, bool)

    def test_magnitude(self):
        """2. Test magnitut de les estrelles
        """
        color1 = self.object.get_color_from_mag(21)
        color2 = self.object.get_color_from_mag(-1.44)
        color3 = self.object.get_color_from_mag(5)

        self.assertEqual(color1, glm.vec3(0,0,0))
        self.assertEqual(color2, glm.vec3(1,1,1))
        
        self.assertGreater(color3.x, 0)
        self.assertLess(color3.x, 1)
        self.assertGreater(color3.y, 0)
        self.assertLess(color3.y, 1)
        self.assertGreater(color3.z, 0)
        self.assertLess(color3.z, 1)
    
    def test_parsing_constellations(self):
        """3. Test de com es generen les constel·lacions
        """
        constellations = self.object.parse_constellations()

        self.assertIsInstance(constellations, dict)
        self.assertTrue(len(constellations) > 0)
        for constellation in constellations:
            self.assertTrue(len(constellations[constellation]) > 0)

if __name__ == '__main__':
    unittest.main()
