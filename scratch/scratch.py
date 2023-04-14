import geotable
from collections import defaultdict
from nmk.plotter import plot_3d
import numpy as np

file = geotable.load("Data/kmls/132kV_Axpo_SBB_Leitungen_Aarau_Rupperswil_IST_Zustand_ohne_SBB_UL.kml")

results = defaultdict(list)
for r in range(226):
    row = file.iloc[r]
    geomtype = row.geometry_object.geom_type

    if geomtype == 'MultiLineString':
        continue
        results[geomtype].append(row.geometry_object.coords._coords)

    if geomtype == "Point":
        results[geomtype].append(row.geometry_object.coords._coords[0])

results["Point"] = np.array(results["Point"])
        
print("asd")