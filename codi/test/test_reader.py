import unittest
import sys
import os
import pandas as pd

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from reader import Reader

class TestReader(unittest.TestCase):
    __slots__ = ('reader1', 'reader2', 'reader3')
    def setUp(self):
        """Crea una instància de Reader
        """
        # Initialize a Light object before each test
        self.reader1 = Reader("data/planets.csv")
        self.reader2 = Reader("data/stars.csv")
        self.reader3 = Reader("data/satellites.csv")

    def test_initialization(self):
        """1. Test d'inicialització de la classe
        """
        # Test if the Reader is initialized with no problems
        self.assertIsInstance(self.reader1, Reader)
        self.assertIsInstance(self.reader2, Reader)
        self.assertIsInstance(self.reader3, Reader)
        self.assertIsInstance(self.reader1.data_path, str)
        self.assertIsInstance(self.reader2.data_path, str)
        self.assertIsInstance(self.reader3.data_path, str)

    def test_read_data(self):
        """2. Test de la lectura i obtenció de dades
        """
        # Test whether the Reader reads the data with no problems, and its data is correctly
        self.reader1 = Reader.read_planets("data/planets.csv", "Mars")
        self.reader2 = Reader.read_stars("data/stars.csv")
        self.reader3 = Reader.read_satellites("data/satellites.csv")

        self.assertIsInstance(self.reader1.data, pd.Series)
        self.assertIsInstance(self.reader2.data, pd.DataFrame)
        self.assertIsInstance(self.reader3.data, pd.DataFrame)

        self.assertEqual((list(self.reader1.data.index)), ['Planet', 
                                                        'Color', 
                                                        'Mass (10^24kg)', 
                                                        'Diameter (km)', 
                                                        'Density (kg/m^3)', 
                                                        'Surface Gravity(m/s^2)', 
                                                        'Escape Velocity (km/s)', 
                                                        'Rotation Period (hours)', 
                                                        'Length of Day (hours)', 
                                                        'Distance from Sun (10^6 km)', 
                                                        'Perihelion (10^6 km)', 
                                                        'Aphelion (10^6 km)', 
                                                        'Orbital Period (days)', 
                                                        'Orbital Velocity (km/s)', 
                                                        'Orbital Inclination (degrees)', 
                                                        'Orbital Eccentricity', 
                                                        'Obliquity to Orbit (degrees)', 
                                                        'Mean Temperature (C)', 
                                                        'Surface Pressure (bars)', 
                                                        'Number of Moons', 
                                                        'Ring System?', 
                                                        'Global Magnetic Field?', 
                                                        'Surface Temperature (C)', 
                                                        'Atmospheric Composition', 
                                                        'Atmospheric Pressure (bars)', 
                                                        'Surface Features', 
                                                        'Composition'])
        self.assertEqual((list(self.reader2.data.columns)), ['x', 'y', 'z', 'mag', 'con', 'proper'])
        self.assertEqual((list(self.reader3.data.columns)), ['planet', 
                                                             'name',
                                                             'radius',
                                                             'Distance_to_planet (10^6km)',
                                                             'Velocity (km/s)'])                          

if __name__ == '__main__':
    unittest.main()
