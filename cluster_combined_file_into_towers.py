# input is a sequence of json files that contain lines and points for a few towers but they are not separate. We separate each tower into a separate file

import os.path
from typing import List, Dict, Union, Any

import numpy as np
from sklearn.cluster import KMeans
import numpy
from glob import glob
from nmk.helper import jsonload, jsondump

folder_path: str = "/mnt/00A03D3C0BCCF8D8/Data/PowerLinesData/20230703Flynex50HZ/50EL_U32_DHHN92/4326"
files: List[str] = glob(os.path.join(folder_path, "*.json"))
clusters: List[int] = [3, 2, 5, 6, 3]
baseJson: Dict[str, Union[str, List[Any]]] = {
"type": "FeatureCollection",
"name": "",
"features": []
}

for file_counter, single_file in enumerate(files):
    all_features: List[Dict] = jsonload(single_file)["features"]

    point_features: List[Any] = [f["geometry"]["coordinates"][:2] if f["geometry"]["type"] == "Point" else f["geometry"]["coordinates"][0][:2] for f in all_features]

    model: KMeans = KMeans(n_clusters = clusters[file_counter], init = "k-means++", n_init=200, max_iter= 500, tol= 1e-8)
    model.fit(X = np.asarray(point_features))
    groups: List[List[Any]] = [[] for i in range(clusters[file_counter])]

    feature: Dict
    feature_it: int
    for feature_it, feature in enumerate(all_features):
        groups[model.labels_[feature_it]].append(feature)

    for i, tower_features in enumerate(groups):
        file_name = os.path.splitext(os.path.basename(single_file))[0] + f"_{i}.geojson"
        write_path: str = os.path.join(folder_path, "output", file_name)
        new_json = baseJson.copy()
        new_json["name"] = os.path.basename(single_file)
        new_json["features"] = tower_features
        jsondump(write_path, new_json)

    print("Completed! ")