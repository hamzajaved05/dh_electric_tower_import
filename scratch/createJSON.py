import json
import pandas as pd
from tower.util import build_single_tower

    


N_towers = 5
long_lats = [[51.7592698044129,	11.0699513905896],
            [51.7594169529938,	11.0661775009908],
            [51.7595768434602,	11.0620710701219],
            [51.7597465400334,	11.0577117901017],
            [51.7598950229959,	11.0538902852527]]

ASLs = [149.26, 160.96, 187.50, 192.65, 175.82]
TopASLs = [165.43, 188.20, 216.70, 221.82, 205.01]


# long_lats = [[53.7522, 10.09653],
#             [53.75227, 10.09582]]

# ASLs = [149.26, 160.96]
# TopASLs = [165.43, 188.20]

json_object = {
    "type": "FeatureCollection",
    "features": []}

Maste = pd.read_excel(io = "Data/CSV/Maste.xlsx", sheet_name = "Maste").iloc[:5]
Traversen = pd.read_excel(io = "Data/CSV/Maste.xlsx", sheet_name = "Traversen")

TowerNames = sorted(list(Maste["Mastnummer"]))
filt = Traversen["Mastnummer"].isin(TowerNames)
Traversen = Traversen[filt]



for name, long_lat, asl, topasl in zip(TowerNames, long_lats, ASLs, TopASLs):
    TowerData = Traversen[Traversen["Mastnummer"] == name].iloc[:, 2:7]
    x = build_single_tower(name, long_lat, asl, topasl, TowerData)
    json_object["features"].append(x)


with open("Data/json/Westnetz.json", "w") as f:
    json.dump(json_object, f)

print("Completed and Saved")