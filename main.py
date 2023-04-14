import pandas as pd
from tower.tower_excel import TowerExcel
from tower.tower_json import TowerGeoJSON
import json
import os
from utils.addWires import addLines
from typing import List
import geojson


SUPPORTED_FORMATS_CSV = ['.csv', '.xlsx']
SUPPORTED_FORMATS_JSON = ['.geojson']

def main():
    dir: str = "Data/50Hz_json"
    outdir: str = dir
    files: List[str]  = [file for file in os.listdir(dir)]
    for file in files:
        json_object = {
            "type": "FeatureCollection",
            "features": []
            }
        
        if os.path.splitext(file)[1] in SUPPORTED_FORMATS_CSV:
            basename = os.path.splitext(os.path.basename(file))[0]
            file = os.path.join(dir, file)
            data = pd.read_excel(file, index_col=0)
            TowerIDs = pd.unique(data["technplatz"])

            towers = []

            for tID in TowerIDs:
                oneTowerData = data[data["technplatz"] == tID]
                tower = TowerExcel(data=oneTowerData)
                towers.append(tower)

                json_data = tower.generate_json_file()

                if len(tower.JSON) == 0:
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
            json_object["features"].append(json_data)

            
        
        else: 
            continue
            
        outfile = os.path.join(outdir, basename+"_n.json")

        json_object = addLines(json_object)
    
        with open(outfile, "w") as f:
            json.dump(json_object, f, indent = 4)

            




if __name__ == "__main__":
    main()