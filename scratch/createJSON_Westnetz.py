import json
import pandas as pd
from tower.util import build1_tower

    
N_towers = 4
long_lats = [
    [50.889301,8.014185],
    [50.89129,8.012411],
    [50.893269,8.010646],
    [50.895237,8.008891]
    ]

TopASLs = [361.799987792969, 362.309997558594, 376.940002441406, 367.970001220703]
ASLs = [331.890014648438, 327.190002441406, 347.059997558594, 329.859985351563]
Azimuths = [45, 60, 60, 60]

json_object = {
    "type": "FeatureCollection",
    "features": []}

Maste = pd.read_excel(io = "Data/Westnetz/MasteWestnetz.xlsx", sheet_name = "Maste").iloc[:4]
Traversen = pd.read_excel(io = "Data/Westnetz/MasteWestnetz.xlsx", sheet_name = "Traversen")

TowerNames = sorted(list(Maste["Mastnummer"]))
filt = Traversen["Mastnummer"].isin(TowerNames)
Traversen = Traversen[filt]

for name, long_lat, asl, topasl, azi in zip(TowerNames, long_lats, ASLs, TopASLs, Azimuths):
    TowerData = Traversen[Traversen["Mastnummer"] == name].iloc[:, 2:7][:7]
    x = build1_tower(name, long_lat, asl, topasl, TowerData, sequence ="A_B_C_D_E_F_G_", AZIMUTH= azi)
    json_object["features"].append(x)


with open("Data/json/Westnetz.json", "w") as f:
    json.dump(json_object, f)

print("Completed and Saved")