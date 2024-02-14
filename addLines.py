from namak.helper import jsonload, jsondump

from utils.addWires import addLines

if __name__ == "__main__":
    path = "/media/hamzawl/Flux/Data/PowerLinesData/20240205AXPO/output/new.json"
    path2 = "/media/hamzawl/Flux/Data/PowerLinesData/20240205AXPO/output/new2.json"
    force_connect_towers = {"Tragwerk 01A": "Tragwerk 02",
                            "Tragwerk 01B": "Tragwerk 02",
                            "Tragwerk 16A": "Tragwerk 15",
                            "Tragwerk 16B": "Tragwerk 15"}

    json_ = jsonload(path)
    jsonLines = addLines(json_, ignore_calib=True, force_connect_towers=force_connect_towers)
    jsondump(path2, jsonLines)
