import os
from typing import Dict
import numpy as np
from nmk.GeoUtils import CartesianMetersToGeo

class POI(object):
    def __init__(self, height: float, distance: float = 0, azimuth: float = 0, calibration: bool = False):
        if distance < 0:
            distance = -distance
            azimuth = (azimuth + 180)
        self.distance = 0 if distance == None else distance
        self.height = height if height == None else height
        self.azimuth = 0 if azimuth == None else azimuth % 360
        self.calibration = calibration
    
    def jsonify(self) -> Dict:
        if self.calibration:
            return {"type": "CALIBRATION",
                    "height": float(self.height),
                    "distance": float(self.distance),
                    "azimuth": float(self.azimuth)}  
                
        else:
            return {"height": float(self.height),
                    "distance": float(self.distance),
                    "azimuth": float(self.azimuth),
                    "wireAzimuth1": float(-self.azimuth),
                    "wireAzimuth2": float(self.azimuth)}

    def get_hash(self) -> float:
        return self.azimuth*32.5+ self.distance*32.1+ self.height*32.9 + 32.4 * (1.92 if self.calibration else 0)

    def __repr__(self) -> str:
        return f"{'Calibration ' if self.calibration else ''}POI at distance {self.distance} with height {self.height} and angle {self.azimuth}"
    
    def set_azimuth(self, azimuth) -> None:
        self.azimuth = azimuth

    def get_lat_lon(self, towerBase, asl):
        height = self.height + asl
        distance = self.distance
        azimuth = self.azimuth
        aziCCW = (90 - azimuth) % 360
        x = distance * np.cos(np.deg2rad(aziCCW))
        y = distance * np.sin(np.deg2rad(aziCCW))
        out = CartesianMetersToGeo(towerBase, [x, y, height])
        return [out[0], out[1], out[2]]
