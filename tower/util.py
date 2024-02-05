import pandas as pd
import numpy as np
from nmk.GeoUtils import CartesianMetersToGeo, GeoToCartesianMeters
from collections import deque

# AZIMUTH = 93.6

def addPOI(obj, height, distance, azimuth, Calib = False):
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

def checkMatchingPOI(data, towers):
    ret = True
    POIsTower = []
    for id in towers:
        POIsTower.append(getNumberofPoisFromTower(data, id))
    return POIsTower

def getNumberofPoisFromTower(data, tower):
    return len(data["features"][tower]["properties"]["pois"])

def getPOIfromIDs(data, towerID, poiID):
    return getTowerfromID(data, towerID)["properties"]["pois"][poiID]

def getTowerfromID(data, towerID):
    return data["features"][towerID]

def getNamefromID(data, towerID):
    return data["features"][towerID]["properties"]["name"]

def getPOILatLongHeight(data, towerId, poiId):
    Tower = getTowerfromID(data, towerId)
    TowerBase = Tower["geometry"]["coordinates"]
    ASL = Tower["properties"]["poleBaseASLMeters"]

    poi = getPOIfromIDs(data, towerId, poiId)
    height = poi["height"] + ASL
    distance = poi["distance"]
    azimuth = poi["azimuth"]
    aziCCW = (90 - azimuth) % 360
    x = distance * np.cos(np.deg2rad(aziCCW))
    y = distance * np.sin(np.deg2rad(aziCCW))
    out = CartesianMetersToGeo(TowerBase[::-1], [x, y, height])
    return [out[1], out[0], height]

def parabolicFunc(x, a, verticalOffset):
    return x**2 / (4 * a) + verticalOffset

def addLinebetweenTowers(data, t1ID, t2ID, wireID1, wireID2):
    pts = []
    pFirst = getPOILatLongHeight(data, t1ID, wireID1)
    pts.append(pFirst)
    pLast = getPOILatLongHeight(data, t2ID, wireID2)
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
    S1 = w_T * x1**2 / 2
    S2 = w_T * x2**2 / 2

    # For parabolic parametrization
    a = x2 **2 / (4 * S2)
    vectorizeParabolic = np.vectorize(parabolicFunc)
    heights = vectorizeParabolic(np.linspace(-x1, x2, count), a, pFirst[2] - S1)
    smallpoints = np.stack([xInterpolated, yInterpolated, heights]).T
    pts.extend(smallpoints.tolist())
    pts.append(pLast)
    return pts


def TowerIDSJson(data):
    return [idx for idx, d in enumerate(data["features"]) if d["properties"]["type"] == "electric_pole"]


def getrecursiveTowerSequence(coordinates, visited, remaining, distance):
    if len(remaining) == 0:
        return visited, distance
    else:
        distances = [np.linalg.norm(getDistanceBetweenTowerIDS(coordinates, visited[-1], tID)) for tID in remaining]
        minIndex = np.argmin(distances)
        visited.append(remaining[minIndex])
        remaining.remove(remaining[minIndex])
        return getrecursiveTowerSequence(coordinates, visited, remaining, distance + np.min(distances))


def getDistanceBetweenTowerIDS(coordinatesMap, tID1, tID2):
    return GeoToCartesianMeters(coordinatesMap[tID1][::-1], coordinatesMap[tID2][::-1])

def sortTowerIDsByDistance(data, tids):
    coordinates = {tid: data["features"][tid]["geometry"]["coordinates"] for tid in tids}

    # distanceMatrix = [[(getDistanceBetweenTowerIDS(coordinates, i, j)) for j in coordinates.keys()] for i in coordinates.keys()] 

    sequenceWRTStart = {}
    for Id in coordinates.keys():
        remaining = list(coordinates.keys())
        visited = [Id]
        remaining.remove(Id)
        visited, distance = getrecursiveTowerSequence(coordinates, visited, remaining, 0)
        sequenceWRTStart[Id] = {"sequence": visited, "distance" : distance}
        
    sequence = min(sequenceWRTStart.values(), key = lambda f: f["distance"])["sequence"]
    return sequence

def addLinefromRows(obj, r1, r2, ASL, azi):
    if len(r1) == 0:
        r1, r2 = r2, r1

    d1 = getxycoordinate(r1, azi)
    if len(r2) == 0:
        d2 = [0, 0, d1[2]]
    else:
        d2 = getxycoordinate(r2, azi)
    d1[2] -= ASL
    d2[2] -= ASL
    addLine(obj, d1, d2)
    return True

def addLine(obj, d1, d2):
    obj["properties"]["structure"]["lines3d"].append([d1, d2])
    return True

def getrowData(row, azi):
    name = row["Mastnummer"]
    height = row["T-Höhe"]
    distance = row["T-Breite"]
    pos = len(row["T-Winkel"]) == 3
    angle = azi if pos else (azi + 180) % 360
    return name, height, distance, angle 

def getxycoordinate(row, azi):
    name, height, distance, angle = getrowData(row.iloc[0], azi)
    angle  = 90 - angle
    x = distance * np.cos(np.deg2rad(angle))
    y = distance * np.sin(np.deg2rad(angle))
    z = height
    return [x, y, z]

def addAllLines(Pois, obj, ASL, azi, sequence):
    for i, j in zip(sequence[:-1], sequence[1:]):
        RowI = Pois[Pois["Seil"] == i]
        RowJ = Pois[Pois["Seil"] == j]
        addLinefromRows(obj, RowI, RowJ, ASL, azi)
    
    return True


def build1Tower(name, long_lat, ASL, ASL_top, Pois, sequence, AZIMUTH):
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
    
    name, topHeight, distance, angle = getrowData(Pois[Pois["Seil"] == "G"].iloc[0], AZIMUTH)
    name, lineHeight, distance, angle = getrowData(Pois[Pois["Seil"] == "A"].iloc[0], AZIMUTH)
    addPOI(features,  topHeight - ASL, 0, 0, True)
    addLine(features, [0, 0, 0], [0, 0, topHeight - ASL])


    for _, row in Pois.iterrows():
        name, height, distance, angle = getrowData(row, AZIMUTH)
        addPOI(features, height - ASL, distance, angle, False)
    
    addAllLines(Pois, features, ASL, (AZIMUTH), sequence)


    return features

def toXY(distance, Azimuth, height):
    return np.array([distance*np.cos(Azimuth), distance*np.sin(Azimuth), height])