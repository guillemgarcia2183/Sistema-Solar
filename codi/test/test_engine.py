import unittest
import sys
import os

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from engine import GraphicsEngine
from camera import Camera, FollowCamera
from gui import ButtonManager
from light import Light
from objects import *

class TestEngine(unittest.TestCase):
    __slots__ = ('object')
    def setUp(self):
        """Crea una instància de Planet
        """
        # Initialize GraphicsEngine object before each test
        self.object = GraphicsEngine(testing=True)

    def test_initialization(self):
        """1. Test d'inicialització de la classe
        """
        # Test if the GraphicsEngine is initialized with no problems
        self.assertIsInstance(self.object, GraphicsEngine)
        self.assertIsInstance(self.object.camera, Camera)
        self.assertIsInstance(self.object.second_cam, FollowCamera)
        self.assertIsInstance(self.object.light, Light)
        self.assertIsInstance(self.object.objects, list)
        self.assertIsInstance(self.object.time, int)
        self.assertIsInstance(self.object.button_manager, ButtonManager)
        self.assertIsInstance(self.object.info, str)
        self.assertIsInstance(self.object.ellipse, bool)

    def test_objects_creation(self):
        """2. Test de la creació d'objectes
        """
        self.object.objects = []
        self.object.create_objects()
        self.assertGreater(len(self.object.objects), 0)
        self.assertTrue(any(type(obj) is Sun for obj in self.object.objects))
        self.assertTrue(any(type(obj) is Planet for obj in self.object.objects))
        self.assertTrue(any(type(obj) is Satellite for obj in self.object.objects))
        self.assertTrue(any(type(obj) is AsteroidBatch for obj in self.object.objects))
        self.assertTrue(any(type(obj) is RingBatch for obj in self.object.objects))

    def test_time(self):
        """3. Test temps
        """
        self.object.time = 0 
        self.object.get_time()
        self.assertGreater(self.object.time, 0)

if __name__ == '__main__':
    unittest.main()
