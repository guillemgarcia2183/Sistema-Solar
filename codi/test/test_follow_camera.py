import unittest
import sys
import os
import glm

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from engine import GraphicsEngine
from camera import FollowCamera
from objects import *

class TestFollowCamera(unittest.TestCase):
    __slots__ = ('camera')
    def setUp(self):
        """Crea una instància de FollowCamera
        """
        # Initialize a Camera object before each test
        self.camera = FollowCamera(GraphicsEngine(testing=True))

    def test_initialization(self):
        """1. Test d'inicialització de la classe
        """
        # Test if the camera is initialized with no problems
        self.assertIsInstance(self.camera, FollowCamera)
        self.assertIsInstance(self.camera.app, GraphicsEngine)
        self.assertIsInstance(self.camera.elevation, int)
        self.assertIsInstance(self.camera.azimuth, int)
        self.assertIsInstance(self.camera.distance, int)
        self.assertIsInstance(self.camera.lock_target, bool)
        self.assertIsInstance(self.camera.relative_position, glm.vec3)
        self.assertIsInstance(self.camera.right, glm.vec3)
        self.assertIsInstance(self.camera.keep_up, bool)
        self.assertIsInstance(self.camera.direction, glm.vec3)
    
    def test_target_selection(self):
        """2. Test de selecció del planeta
        """
        initial_distance = self.camera.distance
        initial_speed =self.camera.speed
        targets = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
        for tg in targets:
            self.camera.select_target(tg)
            self.assertIsInstance(self.camera.target, Planet)
            self.assertNotEqual(self.camera.speed, initial_speed)
            self.assertNotEqual(self.camera.distance, initial_distance)

        

if __name__ == '__main__':
    unittest.main()
