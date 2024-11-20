import pandas as pd


class Reader():

    __slots__ = (
        "data_path", 
        "_data", 
        "_iter"
    )

    def __init__(self, data_path):
        self.data_path = data_path
        self._data = None

    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, new_data):
        self._data = new_data

    @staticmethod
    def read_stars(data_path: str):
        stars = Reader(data_path)
        stars.data = pd.read_csv(data_path)
        stars.data = stars.data[["x", "y", "z", "mag", "con", "proper"]] 
        return stars

    @staticmethod
    def read_planets(data_path: str, name: str):
        planets = Reader(data_path)
        planets.data = pd.read_csv(data_path)
        planets.data = planets.data[planets.data["Planet"] == name].iloc[0]
        return planets
    
    @staticmethod
    def read_satellites(data_path: str):
        satellites = Reader(data_path)
        satellites.data = pd.read_csv(data_path)
        satellites.data = satellites.data[["planet", "name", "radius", "Distance (10^6km)", "Velocity (km/s)"]]
        return satellites


    def __iter__(self):
        self._iter = self._data.itertuples(index=False)
        return self

    def __next__(self):
        row = next(self._iter)
        # NOTE: It is very important that we change dataset(x, y ,z) -> (y, z, x)
        # because of the way star coordinates are described
        return row.y, row.z, row.x, row.mag, row.con, row.proper
    
    def make_stars(self, star_object, args):
        stars = star_object(*args, self)
        return stars