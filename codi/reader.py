import pandas as pd


class Reader():
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
        # Per ara nomes les coordenades i les n primeres estrelles
        stars.data = stars.data[["x", "y", "z"]].head(5000)
        return stars

    @staticmethod
    def read_planets(data_path: str, name: str):
        planets = Reader(data_path)
        planets.data = pd.read_csv(data_path)
        # Per ara nomes les coordenades i les n primeres estrelles
        planets.data = planets.data[planets.data["Planet"] == name].iloc[0]
        return planets

    def __iter__(self):
        self._iter = self._data.itertuples(index=False)
        return self

    def __next__(self):
        row = next(self._iter)
        # NOTE: It is very important that we change dataset(x, y ,z) -> (y, z, x)
        # because of the way star coordinates are described
        return row.y, row.z, row.x
    
    def make_stars(self, star_object, args):
        stars = star_object(*args, self)
        return stars
