import numpy as np
from namak.GeoUtils import CartesianMetersToGeo
import json
import tower.util

from collections import deque
from scipy.optimize import linear_sum_assignment

# inputFile = "Data/json/EONDemo.json"
# with open(inputFile, "r") as f:
#     data = json.load(f)

def addLines(data, ignore_calib = False):
    TowerIDS = tower.util.tower_ids_json(data)
    if len(TowerIDS) <= 1: return data
    sortTowerIDS = tower.util.sort_tower_ids_by_distance(data, TowerIDS)

    pois = tower.util.check_matching_poi(data, TowerIDS)  # noqa: F841

    for tID1, tID2 in zip(sortTowerIDS[:-1], sortTowerIDS[1:]):
        pois_count = min(tower.util.get_numberof_pois_from_tower(data, tID1), tower.util.get_numberof_pois_from_tower(data, tID2))
        T1name = tower.util.get_tower_from_id(data, tID1)["properties"]["name"]
        T2name = tower.util.get_tower_from_id(data, tID2)["properties"]["name"]
        T1GUID = tower.util.get_tower_from_id(data, tID1)["properties"]["guid"]
        T2GUID = tower.util.get_tower_from_id(data, tID2)["properties"]["guid"]

        wires = []

        # Linear sum assignment to match wires
        cost_matrix = calculate_cost_matrix(data, tID1, tID2)
        r_ind, c_ind = linear_sum_assignment(cost_matrix)

        for wireID1, wireID2 in zip(r_ind, c_ind):
            poi1 = tower.util.get_poi_from_ids(data, tID1, wireID1)
            poi2 = tower.util.get_poi_from_ids(data, tID2, wireID2)

            if  ignore_calib and poi1['type'] == "CALIBRATION" and poi2['type'] == "CALIBRATION":
                continue

            wire = tower.util.add_linebetween_towers(data, tID1, tID2, wireID1, wireID2)
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
    number_pois_tower1 = tower.util.get_numberof_pois_from_tower(data, tID1)
    pois_tower1 = [tower.util.get_poi_lat_long_height(data, tID1, pID) for pID in range(number_pois_tower1)]

    number_pois_tower2 = tower.util.get_numberof_pois_from_tower(data, tID2)
    pois_tower2 = [tower.util.get_poi_lat_long_height(data, tID2, pID) for pID in range(number_pois_tower2)]

    cost_matrix = np.asarray([[tower.util.GeoToCartesianMeters(poi1, poi2) for poi2 in pois_tower2] for poi1 in pois_tower1])
    cost_matrix = np.linalg.norm(cost_matrix, axis = 2)
    return cost_matrix