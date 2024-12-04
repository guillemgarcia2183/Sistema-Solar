import pandas as pd
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

class Reader():
    """Classe que llegeix les dades dels datasets."""
    __slots__ = (
        "data_path", 
        "_data", 
        "_iter"
    )

    def __init__(self, data_path):
        """Inicialització de la classe Reader

        Args:
            data_path (str): Path del dataset
        """
        self.data_path = data_path
        self._data = None

    @property
    def data(self):
        """Obtenir dades del dataset."""
        return self._data
    
    @data.setter
    def data(self, new_data):
        """Set variable _data"""
        self._data = new_data

    @staticmethod
    def read_stars(data_path: str):
        """Lectura del dataset d'estrelles

        Args:
            data_path (str): Path del dataset d'estrelles

        Returns:
            Reader: Classe Reader creada amb l'informació del dataset
        """
        stars = Reader(data_path)
        stars.data = pd.read_csv(data_path)
        stars.data = stars.data[["x", "y", "z", "mag", "con", "proper"]]
        return stars

    @staticmethod
    def read_planets(data_path: str, name: str):
        """Lectura del dataset dels planetes

        Args:
            data_path (str): Path del dataset dels planetes

        Returns:
            Reader: Classe Reader creada amb l'informació del dataset
        """
        planets = Reader(data_path)
        planets.data = pd.read_csv(data_path)
        planets.data = planets.data[planets.data["Planet"] == name].iloc[0]
        return planets
    
    @staticmethod
    def read_satellites(data_path: str):
        """Lectura del dataset de satèl·lits

        Args:
            data_path (str): Path del dataset de satèl·lits

        Returns:
            Reader: Classe Reader creada amb l'informació del dataset
        """
        satellites = Reader(data_path)
        satellites.data = pd.read_csv(data_path)
        satellites.data = satellites.data[["planet", "name", "radius", "Distance_to_planet (10^6km)", "Velocity (km/s)"]]
        return satellites


    def __iter__(self):
        """Iterador dels datasets"""
        self._iter = self._data.itertuples(index=False)
        return self

    def __next__(self):
        """Obtenció de la següent fila del dataset d'estrelles"""
        row = next(self._iter)
        # NOTE: It is very important that we change dataset(x, y ,z) -> (y, z, x)
        # because of the way star coordinates are described
        return row.y, row.z, row.x, row.mag, row.con, row.proper
    
    def make_stars(self, star_object, *args, **kwargs):
        """Creació de les estrelles"""
        stars = star_object(*args, self, **kwargs)
        return stars
