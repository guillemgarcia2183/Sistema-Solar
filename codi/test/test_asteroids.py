import unittest
import sys
import os
import time
import numpy as np

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from engine import GraphicsEngine
import shaders as sh
from objects import *

class TestAsteroids(unittest.TestCase):
    __slots__ = ('object')
    def setUp(self):
        """Crea una instància de AsteroidBatch
        """
        self.object = AsteroidBatch(GraphicsEngine(testing = True),
                    [sh.vertex_shader_ASTEROID, sh.fragment_shader_ASTEROID],
                    "textures/asteroids.jpg",  # You'll need an asteroid texture
                    [0.5, 5, 5],  # Adjust these parameters as needed
                    num_asteroids= 1000,  # Or however many you want
                    distance1=15.5,
                    distance2=30.5,
                    velocity=10.0,
                    eccentricity=0.05,
                    type="Trojan Left"
        )

    def test_initialization(self):
        """1. Test d'inicialització de la classe
        """
        # Test if the AsteroidBatch is initialized with no problems
        self.assertIsInstance(self.object, AsteroidBatch)
        self.assertIsInstance(self.object.distance1, float)
        self.assertIsInstance(self.object.distance2, float)
        self.assertIsInstance(self.object.num_asteroids, int)
        self.assertIsInstance(self.object.velocity, float)
        self.assertIsInstance(self.object.eccentricity, float)
        self.assertIsInstance(self.object.type, str)

    def test_collisions(self):
        """2. Test col·lisió asteroides
        """
        # Test if the asteroids collide with each other
        asteroid = self.object.positions[0]
        indices, distances = self.object.find_neighbors(asteroid)
        self.assertEqual(len(indices), 1)
        self.assertEqual(len(distances), 1)
        
        collisions = self.object.check_collisions()
        for tuple in collisions:
            self.assertEqual(len(tuple), 2)
        
        original_positions = self.object.positions

        self.object.update_orbit()
        test1_positions = self.object.positions

        self.object.positions = original_positions
        self.object.apply_collision(collisions)
        self.object.smooth_angle_adjustments()
        self.object.update_orbit()
        test2_positions = self.object.positions

        self.assertNotEqual(test1_positions, test2_positions) 

    # def test_collisions_time(self):
    #     """3. Comparativa de temps entre mètodes per trobar col·lisions
    #     """
    #     initial_time_kdtree = time.time()
    #     collisions_kdtree = self.object.check_collisions()
    #     final_time_kdtree = time.time() - initial_time_kdtree

    #     initial_time_product = time.time()
    #     collisions_product = self.object.check_collisions_optimized()
    #     final_time_product = time.time() - initial_time_product

    #     print(f"Temps Kd_tree amb {self.object.num_asteroids} asteroides: {final_time_kdtree}")
    #     print(f"Temps Numpy product amb {self.object.num_asteroids} asteroides: {final_time_product}")
        
    #     ##################################### LOGS #####################################
    #     # Temps Kd_tree amb 250 asteroides: 0.027542591094970703
    #     # Temps Numpy product amb 250 asteroides: 0.001001596450805664
    #     # Speedup = 27x

    #     # Temps Kd_tree amb 500 asteroides: 0.09464883804321289
    #     # Temps Numpy product amb 500 asteroides: 0.0035066604614257812
    #     # Speedup = 26,85x

    #     # Temps Kd_tree amb 1000 asteroides: 0.34557580947875977
    #     # Temps Numpy product amb 1000 asteroides: 0.01617884635925293
    #     # Speedup = 21,59x
    #     ##################################################################################

if __name__ == '__main__':
    unittest.main()
