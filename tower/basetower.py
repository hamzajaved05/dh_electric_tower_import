import numpy as np
import pandas as pd
from tower.pointofinterest import POI
from tower.line import Line
from typing import Mapping


class BaseTower(object):
    def __init__(self, *args, **kwargs):
        self.name = None
        self.unique_identifier = None
        self.longitude = None
        self.latitude = None
        self.base_height = None
        self.yaw_angle = None
        self.angle_offset = None
        self.tower_type = None
        self.tower_material = None
        self.json_data = {}
        self.pois: Mapping[str, Line] = {}
        self.lines: Mapping[str, Line] = {}
        self.highest_point = None
        self.data = None

    def generate_json_file(self):
        if len(self.pois) == 0:
            self.calculate_pois()
        if len(self.lines) == 0:
            self.calculate_lines()
        if (len(self.pois) > 1 and not self.highest_point is None):
            self.generate_json()
            return self.json_data

    def generate_json(self):
        self.json_data = {"type": "Feature"}
        self.json_data["geometry"] = {
            "type": "Point",
            "coordinates": [self.longitude, self.latitude]
        }

        pois = [
            poi.jsonify() for poi in self.pois.values()
        ]
        pois = sorted(pois, key=lambda f: f["height"] * 100 + f["distance"] * 10 + f["azimuth"] / 180, reverse=True)

        self.json_data["properties"] = {
            "type": "electric_pole",
            "name": str(self.name),
            "poleBaseASLMeters": self.base_height,
            "pois": pois,
            "structure": {
                "lines3d": [line.jsonify() for line in self.lines.values()]
            }
        }

    def add_poi(self, height, distance, angle, calibration):
        if pd.isnull(height) or pd.isnull(distance) or pd.isnull(angle):
            return False
        p = POI(height, distance, angle, calibration=calibration)
        poi_hash = p.get_hash()
        if poi_hash not in self.pois.keys():
            self.pois[poi_hash] = p

    def __repr__(self) -> str:
        return f"Tower {self.name}  '{self.unique_identifier}' at {self.longitude}, {self.latitude} with POI count = {len(self.pois)}"
    
    def add_line(self, p1, p2):
        


        line = Line(p1, p2)
        hash = line.get_hash()
        if not hash in self.lines.keys():
            self.lines[hash] = line


    def get_value(self, data):
        if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
            return data.iloc[0]
        else:
            return data
        
    
    def calculate_pois(self,):
        raise NotImplementedError
    
    def calculate_lines(self,):
        raise NotImplementedError