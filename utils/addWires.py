import numpy as np
from nmk.GeoUtils import CartesianMetersToGeo
import json
from tower.util import getPOIfromIDs, GeoToCartesianMeters, TowerIDSJson, sortTowerIDsByDistance, checkMatchingPOI, getNumberofPoisFromTower, getTowerfromID, addLinebetweenTowers, getPOILatLongHeight

from collections import deque
from scipy.optimize import linear_sum_assignment

# inputFile = "Data/json/EONDemo.json"
# with open(inputFile, "r") as f:
#     data = json.load(f)

def addLines(data, ignore_calib = False):
    TowerIDS = TowerIDSJson(data)
    if len(TowerIDS) <= 1: return data
    sortTowerIDS = sortTowerIDsByDistance(data, TowerIDS)

    pois = checkMatchingPOI(data, TowerIDS)  # noqa: F841

    for tID1, tID2 in zip(sortTowerIDS[:-1], sortTowerIDS[1:]):
        pois_count = min(getNumberofPoisFromTower(data, tID1), getNumberofPoisFromTower(data, tID2))
        T1name = getTowerfromID(data, tID1)["properties"]["name"]
        T2name = getTowerfromID(data, tID2)["properties"]["name"]
        T1GUID = getTowerfromID(data, tID1)["properties"]["guid"]
        T2GUID = getTowerfromID(data, tID2)["properties"]["guid"]

        wires = []

        # Linear sum assignment to match wires

        cost_matrix = calculate_cost_matrix(data,tID1, tID2)

        r_ind, c_ind = linear_sum_assignment(cost_matrix)

        # for wireId in range(0, pois_count):
        #     wire = addLinebetweenTowers(data, tID1, tID2, wireId, wireID)
        #     wires.append(wire)

        for wireID1, wireID2 in zip(r_ind, c_ind):
            poi1 = getPOIfromIDs(data, tID1, wireID1)
            poi2 = getPOIfromIDs(data, tID2, wireID2)

            if  ignore_calib and poi1['type'] == "CALIBRATION" and poi2['type'] == "CALIBRATION":
                continue

            wire = addLinebetweenTowers(data, tID1, tID2, wireID1, wireID2)
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
                    "connected_towers": [T1GUID, T2GUID]
                }
            },
        )
    return data


def calculate_cost_matrix(data, tID1, tID2):
    number_pois_tower1 = getNumberofPoisFromTower(data, tID1)
    pois_tower1 = [getPOILatLongHeight(data, tID1, pID) for pID in range(number_pois_tower1)]

    number_pois_tower2 = getNumberofPoisFromTower(data, tID2)
    pois_tower2 = [getPOILatLongHeight(data, tID2, pID) for pID in range(number_pois_tower2)]

    cost_matrix = np.asarray([[GeoToCartesianMeters(poi1, poi2) for poi2 in pois_tower2] for poi1 in pois_tower1])
    cost_matrix = np.linalg.norm(cost_matrix, axis = 2)
    return cost_matrix