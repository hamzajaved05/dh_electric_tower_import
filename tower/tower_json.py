 # This code snippet defines a class called TowerGeoJSON that inherits from BaseTower. It initializes the TowerGeoJSON object with JSON data, extracts information from the JSON data, filters the data based on wire direction, calculates points of interest (POIs)
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
        self.base_height = 9999
        self.towerType = None
        self.towerMaterial = None
        self.JSON = {}

        self.get_information_from_json()

    def get_information_from_json(self):
        top_point = self.data["features"][0]['geometry']['coordinates']

        i = 0
        while i < len(self.data["features"]):
            if self.data["features"][i]['geometry']['type'] == 'LineString':
                lowestheight = min(self.data["features"][i]['geometry']['coordinates'][1][2],
                                   self.data["features"][i]['geometry']['coordinates'][0][2])
                highest_height = max(self.data["features"][i]['geometry']['coordinates'][1][2],
                                   self.data["features"][i]['geometry']['coordinates'][0][2])

                if lowestheight < self.base_height:
                    self.longitude = self.data["features"][i]['geometry']['coordinates'][0][0]
                    self.latitude = self.data["features"][i]['geometry']['coordinates'][0][1]
                    self.base_height = lowestheight
                    self.highest_point = highest_height

            i += 1

        return True

    def filterDataBasedonWireDirection(self, data):
        directions = pd.unique(data["seil_richtung"])
        if len(directions) == 0:
            raise Exception("There is no valid incomming outgoing directions")

        return data[data["seil_richtung"] == directions[0]]

    def calculate_pois(self):
        # self.highest_point = 0

        for feature in self.data["features"]:
            if feature['geometry']['type'] == 'Point':
                point = feature['geometry']['coordinates']

                if self.highest_point < point[2]:
                    print(f"Potentially a point higher than the Calibration Point in {self.name} at location: {self.latitude}, {self.longitude} | Poi height {point[2]} vs Highest Point {self. highest_point}")
                    # self.highest_point = point[2]

                if point[2] - self.base_height < 2:
                    print("skipping")
                    continue
                self.get_poi_from_3d_point(point)

        self.add_poi(height=self.highest_point - self.base_height, distance=0, angle=0, calibration=True)

        return True

    def calculate_lines(self):
        # self.add_line([0, 0, 0], [0, 0, self.highest_point - self.base_height])

        for feature in self.data["features"][2:]:
            if feature['geometry']['type'] == 'LineString':
                points = feature['geometry']['coordinates']
                self.add_line(self.getXYlocation(points[0]), self.getXYlocation(points[1]))
        return True

    def getHighestPoint(self, data):
        return np.max(data[["elevation_ausl_hoeheabboden", "seil_realposy"]])

    def get_poi_from_3d_point(self, point):
        cartesian_point = GeoToCartesianMeters([self.latitude, self.longitude], point[:2][::-1])
        angle = 90 - np.arctan2(cartesian_point[1], cartesian_point[0]) * 180 / np.pi
        height = point[2] - self.base_height
        distance = np.linalg.norm(cartesian_point)
        self.add_poi(height=height, distance=distance, angle=angle, calibration=False)

        return True

    def getXYlocation(self, point):
        cartesian_point = GeoToCartesianMeters([self.latitude, self.longitude], point[:2][::-1])
        return [*cartesian_point, point[2] - self.base_height]

    def __repr__(self) -> str:
        return f"Tower {self.name}  '{self.uniqueIdentifier}' at {self.longitude}, {self.latitude} with POI count = {len(self.pois)}"
