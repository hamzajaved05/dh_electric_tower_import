from namak.helper import jsonload, jsondump

from utils.addWires import addLines

if __name__ == "__main__":
    path = "/mnt/00A03D3C0BCCF8D8/Data/PowerLinesData/2023110750HZFullTowerScan/793_raw.json"
    path2 = "/mnt/00A03D3C0BCCF8D8/Data/PowerLinesData/2023110750HZFullTowerScan/793_processed.json"
    json_ = jsonload(path)
    jsonLines = addLines(json_, ignore_calib=True)
    jsondump(path2, jsonLines)
