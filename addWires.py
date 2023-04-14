import numpy as np
from nmk.GeoUtils import CartesianMetersToGeo
import json
from tower.util import *

from collections import deque

# inputFile = "Data/json/EONDemo.json"
# with open(inputFile, "r") as f:
#     data = json.load(f)

def addLines(data):
    TowerIDS = TowerIDSJson(data)
    if len(TowerIDS) <= 1: return data
    sortTowerIDS = sortTowerIDsByDistance(data, TowerIDS)

    pois = checkMatchingPOI(data, TowerIDS)

    for tID1, tID2 in zip(sortTowerIDS[:-1], sortTowerIDS[1:]):
        pois_count = min(getNumberofPoisFromTower(data, tID1), getNumberofPoisFromTower(data, tID2))
        T1name = getTowerfromID(data, tID1)["properties"]["name"]
        T2name = getTowerfromID(data, tID2)["properties"]["name"]
        wires = []
        for wireId in range(0, pois_count):
            wire = addLinebetweenTowers(data, tID1, tID2, wireId)
            wires.append(wire)

        data["features"].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": wires
                },

                # TODO: add properties in each tower pair
                "properties": {
                    "type": "electric_line",
                    "name": "power line",
                    "connected_towers": [T1name, T2name]
                }
            },
        )
    return data
