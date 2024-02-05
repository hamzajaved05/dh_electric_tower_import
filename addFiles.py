import pandas as pd
from tower.tower_excel import TowerExcel
from tower.tower_json import TowerGeoJSON
import json
import os
from utils.addWires import addLines
from typing import List
import geojson
from nmk.helper import checkmkdir


path = "/home/hamzawlptp/Downloads/siegen.json"

with open(file=path, mode="r") as f:
    json_object_load = geojson.load(f)

json_object = addLines(data=json_object_load)


with open("/home/hamzawlptp/Downloads/siegenOutput.json", "w") as f:
    json.dump(json_object, f, indent = 4)
print("Done")