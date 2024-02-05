import pandas as pd
from tower.tower_excel import TowerExcel
from tower.tower_json import TowerGeoJSON
import json
import os
from utils.addWires import addLines
from typing import List
import geojson
from nmk.helper import checkmkdir

from nmk.drone import DroneDirection


SUPPORTED_FORMATS_CSV = ['.csv', '.xlsx']
SUPPORTED_FORMATS_JSON = ['.geojson']

def main():
    """
     Convert tower data to json. This is a python script to convert towes and vectoried data to json
    """
    basename: str = "base"
    dir: str = "/mnt/00A03D3C0BCCF8D8/Data/PowerLinesData/20231006AXPO"
    outdir: str = os.path.join(dir, "output")
    checkmkdir(outdir)
    files: List[str]  = [file for file in os.listdir(dir)]
    json_object = {
    "type": "FeatureCollection",
    "features": []
    } 
    # Generate TowerExcel and TowerGeoJSON features.
    for file in files:
        # Generate a TowerExcel or TowerGeoJSON file.
        if os.path.splitext(file)[1] in SUPPORTED_FORMATS_CSV:
            basename = os.path.splitext(os.path.basename(file))[0]
            file = os.path.join(dir, file)
            data = pd.read_excel(file, index_col=0)
            TowerIDs = pd.unique(data["technplatz"])

            towers = []

            # Generate a JSON file for each of the TowerIDs in the data.
            for tID in TowerIDs:
                oneTowerData = data[data["technplatz"] == tID]
                tower = TowerExcel(data=oneTowerData)
                towers.append(tower)

                json_data = tower.generate_json_file()

                # Add features to the json_object features list
                if len(json_data) == 0:
                    continue
                else:
                    json_object["features"].append(json_data)

        elif os.path.splitext(file)[1] in SUPPORTED_FORMATS_JSON:
            basename = os.path.splitext(os.path.basename(file))[0]
            file = os.path.join(dir, file)
            with open(file, "r") as f:
                json_object_load = geojson.load(f)
            tower = TowerGeoJSON(json_object_load)
            json_data = tower.generate_json_file()
            json_object["features"].append( json_data)

        
        else: 
            continue

    outfile = os.path.join(outdir, basename + "_n.json")
    json_object = addLines(json_object)

    with open(outfile, "w") as f:
        json.dump(json_object, f, indent=4)

# main function for the main module
if __name__ == "__main__":
    main()