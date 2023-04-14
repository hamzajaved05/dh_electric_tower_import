import os

class POI(object):
    def __init__(self, height, distance = 0, azimuth = 0, calibration = False):
        if distance < 0:
            distance = -distance
            azimuth = (azimuth + 180)
        self.distance = 0 if distance == None else distance
        self.height = height if height == None else height
        self.azimuth = 0 if azimuth == None else azimuth % 360
        self.calibration = calibration
    
    def jsonify(self):
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

    def getHash(self):
        return self.azimuth*32.5+ self.distance*32.1+ self.height*32.9 + 32.4 * (1.92 if self.calibration else 0)

    def __repr__(self):
        return f"{'Calibration ' if self.calibration else ''}POI at distance {self.distance} with height {self.height} and angle {self.azimuth}"
    
    def setAzimuth(self, azimuth):
        self.azimuth = azimuth
