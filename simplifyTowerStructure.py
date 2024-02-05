import os
from nmk.helper import jsonload, jsondump
from tower.tower_excel import get_line
from utils.addWires import addLines
import sys

json_path = "/home/hamza_wl/59.json"
data = jsonload(json_path)
def simplifyTowerstruct(data):
    def getFromPois(poi_data):
        lines = []
        for singlePoi in poi_data:
            if singlePoi["type"] == "CALIBRATION":
                lines.append(get_line(0, 0, 0, singlePoi["distance"], singlePoi["azimuth"], singlePoi["height"]))
            else:
                lines.append(get_line(0, 0, singlePoi["height"], singlePoi["distance"], singlePoi["azimuth"],
                                      singlePoi["height"]))
        return lines

    for feat in data["features"]:
        # print(f"{feat['properties']['type']}: {feat['properties']['structure']}")
        if feat["properties"]["type"] == "electric_pole" and len(feat["properties"]["structure"]["lines3d"]) > 15:
            feat["properties"]["structure"]["lines3d"] = getFromPois(feat["properties"]["pois"])

    return data


# data = jsonload(json_path)
data = simplifyTowerstruct(data)
data = addLines(data)
jsondump(
    "/home/hamza_wl/59_1.json",
    data)
print("asd")
