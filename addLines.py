import pandas as pd
from tower.tower_excel import TowerExcel
from tower.tower_json import TowerGeoJSON
import json
import os
from utils.addWires import addLines
from typing import List
import geojson
from nmk.helper import checkmkdir, jsonload, jsondump

if __name__ == "__main__":
        path = "/mnt/00A03D3C0BCCF8D8/Data/PowerLinesData/2023110750HZFullTowerScan/793_raw.json"
        path2 ="/mnt/00A03D3C0BCCF8D8/Data/PowerLinesData/2023110750HZFullTowerScan/793_processed.json"
        json_ = jsonload(path)
        jsonLines = addLines(json_, ignore_calib= True)
        jsondump(path2, jsonLines)