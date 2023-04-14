import numpy as np
import pandas as pd
from tower.pointofinterest import POI
from tower.basetower import BaseTower
from nmk.GeoUtils import GeoToCartesianMeters 


class TowerGeoJSON(BaseTower):
    def __init__(self, json_data: str, *args, **kwargs) -> None:
        super().__init__(self, *args, **kwargs)
        self.data = json_data
        self.name = "0"
        self.uniqueIdentifier = "0"
        self.longitude = None
        self.latitude = None
        self.baseHeight = None
        self.towerType = None
        self.towerMaterial = None
        self.JSON = {}

        self.get_information_from_json()

    def get_information_from_json(self):
        top_point = self.data["features"][0]['geometry']['coordinates']
        self.longitude = top_point[0]
        self.latitude = top_point[1]
        self.base_height = self.data["features"][4]['geometry']['coordinates'][1][2]
        return True

    def filterDataBasedonWireDirection(self, data):
        directions = pd.unique(data["seil_richtung"])
        if len(directions) == 0:
            raise Exception("There is no valid incomming outgoing directions")

        return data[data["seil_richtung"] == directions[0]]

    def calculate_pois(self):
        self.highest_point = 0

        for feature in self.data["features"]:
            if feature['geometry']['type'] == 'Point':
                point = feature['geometry']['coordinates']

                if self.highest_point < point[2]:
                    self.highest_point = point[2]
                self.get_poi_from_3d_point(point)

        self.add_poi(height=self.highest_point - self.base_height, distance=0, angle=0, calibration=True)

        return True

    def calculate_lines(self):

        for feature in self.data["features"]:
            if feature['geometry']['type'] == 'LineString':
                geometry = feature['geometry']['coordinates']
                for index in range(len(geometry)):
                    lat_long_height = [geometry[index][1], geometry[index][0], geometry[index][2]]
                    geometry[index] = GeoToCartesianMeters([self.latitude, self.longitude, self.base_height], lat_long_height)
                self.add_line(geometry[0], geometry[1])

        return True


    def getHighestPoint(self, data):
        return np.max(data[["elevation_ausl_hoeheabboden", "seil_realposy"]])
    
    def get_poi_from_3d_point(self, point):
        cartesian_distance = GeoToCartesianMeters([self.latitude, self.longitude], point[:2][::-1])
        angle = 90 - np.arctan2(cartesian_distance[1], cartesian_distance[0]) * 180 / np.pi
        height = point[2] - self.base_height
        distance = np.linalg.norm(cartesian_distance)
        self.add_poi(height=height, distance=distance, angle=angle, calibration=False)

        return True

    def __repr__(self) -> str:
        return f"Tower {self.name}  '{self.uniqueIdentifier}' at {self.longitude}, {self.latitude} with POI count = {len(self.pois)}"