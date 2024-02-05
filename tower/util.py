import pandas as pd
import numpy as np
from namak.GeoUtils import CartesianMetersToGeo, GeoToCartesianMeters
from collections import deque


# AZIMUTH = 93.6

def add_poi(obj, height, distance, azimuth, Calib=False):
    if Calib:
        poi = {"type": "CALIBRATION",
               "height": height,
               "distance": distance,
               "azimuth": azimuth}
    else:
        poi = {"height": height,
               "distance": distance,
               "azimuth": azimuth,
               "wireAzimuth1": -azimuth,
               "wireAzimuth2": azimuth}

    obj["properties"]["pois"].append(poi)
    return True


def check_matching_poi(data, towers):
    ret = True
    POIsTower = []
    for id in towers:
        POIsTower.append(get_numberof_pois_from_tower(data, id))
    return POIsTower


def get_numberof_pois_from_tower(data, tower):
    return len(data["features"][tower]["properties"]["pois"])


def get_poi_from_ids(data, towerID, poiID):
    return get_tower_from_id(data, towerID)["properties"]["pois"][poiID]


def get_tower_from_id(data, towerID):
    return data["features"][towerID]


def getNamefromID(data, towerID):
    return data["features"][towerID]["properties"]["name"]


def get_poi_lat_long_height(data, towerId, poiId):
    Tower = get_tower_from_id(data, towerId)
    TowerBase = Tower["geometry"]["coordinates"]
    ASL = Tower["properties"]["poleBaseASLMeters"]

    poi = get_poi_from_ids(data, towerId, poiId)
    height = poi["height"] + ASL
    distance = poi["distance"]
    azimuth = poi["azimuth"]
    aziCCW = (90 - azimuth) % 360
    x = distance * np.cos(np.deg2rad(aziCCW))
    y = distance * np.sin(np.deg2rad(aziCCW))
    out = CartesianMetersToGeo(TowerBase[::-1], [x, y, height])
    return [out[1], out[0], height]


def parabolic_func(x, a, verticalOffset):
    return x ** 2 / (4 * a) + verticalOffset


def add_linebetween_towers(data, t1ID, t2ID, wireID1, wireID2):
    pts = []
    pFirst = get_poi_lat_long_height(data, t1ID, wireID1)
    pts.append(pFirst)
    pLast = get_poi_lat_long_height(data, t2ID, wireID2)
    count = 10

    xInterpolated, yInterpolated = np.linspace(pFirst[0], pLast[0], count), np.linspace(pFirst[1], pLast[1], count)
    h = pLast[2] - pFirst[2]
    w_T = 5e-4
    L = GeoToCartesianMeters(pFirst[:2][::-1], pLast[:2][::-1])
    L_ = np.linalg.norm(L)

    # h can be negative and hence the x1 and x2 can flip | It is needed
    x1 = L_ / 2 - (h / L_) / w_T
    x2 = L_ / 2 + (h / L_) / w_T

    # S1 is sag from the closer side | S2 from the other side
    S1 = w_T * x1 ** 2 / 2
    S2 = w_T * x2 ** 2 / 2

    # For parabolic parametrization
    a = x2 ** 2 / (4 * S2)
    vectorizeParabolic = np.vectorize(parabolic_func)
    heights = vectorizeParabolic(np.linspace(-x1, x2, count), a, pFirst[2] - S1)
    smallpoints = np.stack([xInterpolated, yInterpolated, heights]).T
    pts.extend(smallpoints.tolist())
    pts.append(pLast)
    return pts


def tower_ids_json(data):
    return [idx for idx, d in enumerate(data["features"]) if d["properties"]["type"] == "electric_pole"]


def get_recursive_tower_sequence(coordinates, visited, remaining, distance):
    if len(remaining) == 0:
        return visited, distance
    else:
        distances = [np.linalg.norm(get_distance_between_tower_IDS(coordinates, visited[-1], tID)) for tID in remaining]
        minIndex = np.argmin(distances)
        visited.append(remaining[minIndex])
        remaining.remove(remaining[minIndex])
        return get_recursive_tower_sequence(coordinates, visited, remaining, distance + np.min(distances))


def get_distance_between_tower_IDS(coordinatesMap, tID1, tID2):
    return GeoToCartesianMeters(coordinatesMap[tID1][::-1], coordinatesMap[tID2][::-1])


def sort_tower_ids_by_distance(data, tids):
    coordinates = {tid: data["features"][tid]["geometry"]["coordinates"] for tid in tids}

    # distanceMatrix = [[(getDistanceBetweenTowerIDS(coordinates, i, j)) for j in coordinates.keys()] for i in coordinates.keys()] 

    sequenceWRTStart = {}
    for Id in coordinates.keys():
        remaining = list(coordinates.keys())
        visited = [Id]
        remaining.remove(Id)
        visited, distance = get_recursive_tower_sequence(coordinates, visited, remaining, 0)
        sequenceWRTStart[Id] = {"sequence": visited, "distance": distance}

    sequence = min(sequenceWRTStart.values(), key=lambda f: f["distance"])["sequence"]
    return sequence


def add_linefrom_rows(obj, r1, r2, ASL, azi):
    if len(r1) == 0:
        r1, r2 = r2, r1

    d1 = get_xy_coordinate(r1, azi)
    if len(r2) == 0:
        d2 = [0, 0, d1[2]]
    else:
        d2 = get_xy_coordinate(r2, azi)
    d1[2] -= ASL
    d2[2] -= ASL
    add_line(obj, d1, d2)
    return True


def add_line(obj, d1, d2):
    obj["properties"]["structure"]["lines3d"].append([d1, d2])
    return True


def get_row_data(row, azi):
    name = row["Mastnummer"]
    height = row["T-Höhe"]
    distance = row["T-Breite"]
    pos = len(row["T-Winkel"]) == 3
    angle = azi if pos else (azi + 180) % 360
    return name, height, distance, angle


def get_xy_coordinate(row, azi):
    name, height, distance, angle = get_row_data(row.iloc[0], azi)
    angle = 90 - angle
    x = distance * np.cos(np.deg2rad(angle))
    y = distance * np.sin(np.deg2rad(angle))
    z = height
    return [x, y, z]


def add_all_lines(Pois, obj, ASL, azi, sequence):
    for i, j in zip(sequence[:-1], sequence[1:]):
        RowI = Pois[Pois["Seil"] == i]
        RowJ = Pois[Pois["Seil"] == j]
        add_linefrom_rows(obj, RowI, RowJ, ASL, azi)

    return True


def build1_tower(name, long_lat, ASL, ASL_top, Pois, sequence, AZIMUTH):
    features = {"type": "Feature"}
    features["geometry"] = {
        "type": "Point",
        "coordinates": long_lat[::-1]
    }
    features["properties"] = {
        "type": "electric_pole",
        "name": name,
        "poleBaseASLMeters": ASL,
        "pois": [],
        "structure": {
            "lines3d": []}}

    name, topHeight, distance, angle = get_row_data(Pois[Pois["Seil"] == "G"].iloc[0], AZIMUTH)
    name, lineHeight, distance, angle = get_row_data(Pois[Pois["Seil"] == "A"].iloc[0], AZIMUTH)
    add_poi(features, topHeight - ASL, 0, 0, True)
    add_line(features, [0, 0, 0], [0, 0, topHeight - ASL])

    for _, row in Pois.iterrows():
        name, height, distance, angle = get_row_data(row, AZIMUTH)
        add_poi(features, height - ASL, distance, angle, False)

    add_all_lines(Pois, features, ASL, (AZIMUTH), sequence)

    return features

def to_xy(distance, Azimuth, height):
    return np.array([distance * np.cos(Azimuth), distance * np.sin(Azimuth), height])
