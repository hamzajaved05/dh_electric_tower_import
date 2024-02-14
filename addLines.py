from namak.helper import jsonload, jsondump

from utils.addWires import addLines

if __name__ == "__main__":
    path = "/media/hamzawl/Flux/Data/PowerLinesData/20240205AXPO/output/toweraxpo.json"
    path2 = "/media/hamzawl/Flux/Data/PowerLinesData/20240205AXPO/output/toweraxpo2.json"
    force_add = {}

    json_ = jsonload(path)
    jsonLines = addLines(json_, ignore_calib=True)
    jsondump(path2, jsonLines)
