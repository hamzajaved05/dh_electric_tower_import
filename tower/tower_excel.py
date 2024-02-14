import numpy as np
import pandas as pd
from tower.pointofinterest import POI
from tower.basetower import BaseTower


class TowerExcel(BaseTower):
    def __init__(self, axpo=True, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.axpo = axpo
        self.data = kwargs["data"]
        self.name = str(self.data["name"].iloc[0])
        self.uniqueIdentifier = self.data["technplatz"].iloc[0]
        self.longitude = self.data["longitudewgs84"].iloc[0]
        self.latitude = self.data["latitudewgs84"].iloc[0]
        self.base_height = self.data["hoehe"].iloc[0]
        self.yawAngle = self.data["orientation_angle"].iloc[0]
        self.angleOffset = self.data["orient_angle_offset"].iloc[0]
        self.towerType = self.data["masttyp"].iloc[0]
        self.towerMaterial = self.data["mastmaterial"].iloc[0]
        self.JSON = {}

    def filter_data_based_on_wire_direction(self, data):
        directions = pd.unique(data["seil_richtung"])
        if len(directions) == 0:
            raise Exception("There is no valid incoming outgoing directions")

        return data[data["seil_richtung"] == directions[0]]

    def calculate_pois(self):
        self.highest_point = self.get_value(
            self.get_highest_point(self.data))
        self.pois = {}

        uniqueYaws = set()

        for index, row in self.data.iterrows():
            angle = self.yawAngle + 90
            distance = row["seil_realposx"]
            height = row["seil_realposy"]

            # Fixing some bugs in the data (missing data)

            if pd.isnull(height) and not pd.isnull(distance) and not pd.isnull(row["elevation_ausl_hoeheabboden"]):
                height = row["elevation_ausl_hoeheabboden"]

            if abs(distance) > 0.1:
                uniqueYaws.add(angle if distance > 0 else angle + 180)

            if height > self.highest_point:
                self.highest_point = height

            self.add_poi(height=height, distance=distance, angle=angle, calibration=False)

        # Add the highest point as calibration point
        self.add_poi(self.highest_point, 0, 0, calibration=True)

        uniqueYaws = list(uniqueYaws)
        if len(uniqueYaws) == 1:
            for each in self.pois:
                self.pois[each].set_azimuth(uniqueYaws[0])

        return True

    def calculate_lines(self):
        if len(self.pois) == 0:
            print("No POIs found")
            return False

        self.lines = {}
        for index, row in self.data.iterrows():
            leftangle = self.yawAngle - 90.0
            rightangle = self.yawAngle + 90.0
            distanceleft = row["ausleger_breite_links"]
            distanceright = row["ausleger_breite_rechts"]
            height = row["elevation_ausl_hoeheabboden"]
            if pd.isnull(distanceleft) and pd.isnull(distanceright):
                line = get_vertical_line(0.0, self.highest_point)
            else:
                line = get_line(distanceleft, leftangle, height, distanceright, rightangle, height)

            self.add_line(line[0], line[1])

        return True

    def get_highest_point(self, data):
        return np.max(data[["elevation_ausl_hoeheabboden", "seil_realposy"]])

    def __repr__(self) -> str:
        return f"Tower {self.name}  '{self.uniqueIdentifier}' at {self.longitude}, {self.latitude} with POI count = {len(self.pois)}"


def get_vertical_line(heightStart, heightEnd):
    points = [[0, 0, heightStart], [0, 0, heightEnd]]
    return points


def get_line(distance1, angle1, height1, distance2, angle2, height2):
    angle1 = 90 - angle1
    angle2 = 90 - angle2
    x1 = distance1 * np.cos(np.deg2rad(angle1))
    y1 = distance1 * np.sin(np.deg2rad(angle1))
    z1 = height1

    x2 = distance2 * np.cos(np.deg2rad(angle2))
    y2 = distance2 * np.sin(np.deg2rad(angle2))
    z2 = height2
    return [[x1, y1, z1], [x2, y2, z2]]


if __name__ == "__main__":
    file = "Data/AXPO/masteditorexport__TR0112_2023-01-18.xlsx"
    data = pd.read_excel(file, index_col=0)
    TowerIDs = pd.unique(data["technplatz"])

    towers = []

    for tID in TowerIDs:
        oneTowerData = data[data["technplatz"] == tID]
        tower = TowerExcel(data=oneTowerData)
        towers.append(tower)
