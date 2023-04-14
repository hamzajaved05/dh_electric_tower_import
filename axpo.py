import pandas as pd
from tower.tower import Tower
import json
import os
from addWires import addLines

SUPPORTED_FORMATS = ['.csv', '.xlsx']
def main():
    dir = "Data/Tennet_Lammert"
    outdir = "Data/Tennet_Lammert"
    files = [file for file in os.listdir(dir) if os.path.splitext(file)[1] in SUPPORTED_FORMATS]
    for file in files:
        basename = os.path.splitext(os.path.basename(file))[0]
        file = os.path.join(dir, file)
        data = pd.read_excel(file, index_col=0)
        TowerIDs = pd.unique(data["technplatz"])
        
        json_object = {
        "type": "FeatureCollection",
        "features": []}

        towers = []

        for tID in TowerIDs:
            oneTowerData = data[data["technplatz"] == tID]
            tower = Tower(data=oneTowerData)
            towers.append(tower)

            json_data = tower.generate_json_file()

            if len(tower.JSON) == 0:
                continue
            else:
                json_object["features"].append(json_data)

        outfile = os.path.join(outdir, basename+"_n.json")

        json_object = addLines(json_object)
        
        with open(outfile, "w") as f:
            json.dump(json_object, f, indent = 4)




if __name__ == "__main__":
    main()