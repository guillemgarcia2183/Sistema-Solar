import unittest
import sys
import os
import glm

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from engine import GraphicsEngine
from camera import Camera

class TestCamera(unittest.TestCase):
    __slots__ = ('camera')
    def setUp(self):
        """Crea una instància de Camera
        """
        # Initialize a Camera object before each test
        self.camera = Camera(GraphicsEngine(testing=True))

    def test_initialization(self):
        """1. Test d'inicialització de la classe
        """
        # Test if the camera is initialized with no problems
        self.assertIsInstance(self.camera, Camera)
        self.assertIsInstance(self.camera.app, GraphicsEngine)
        self.assertIsInstance(self.camera.aspec_ratio, float)
        self.assertIsInstance(self.camera.sensitivity, float)
        self.assertIsInstance(self.camera.speed, float)
        self.assertEqual(self.camera.up, glm.vec3(0,1,0))

    def test_process_mouse_movement(self):
        """2. Test del moviment del ratolí amb la càmera
        """
        # Test camera movement
        self.camera.yaw = -135.0
        self.camera.pitch = -35.264389682754654
        self.camera.process_mouse_movement(30, 30)
        self.assertAlmostEqual(self.camera.yaw, -132.0, 0.1)
        self.assertAlmostEqual(self.camera.pitch, -38.264389682754654, 0.1)

if __name__ == '__main__':
    unittest.main()
