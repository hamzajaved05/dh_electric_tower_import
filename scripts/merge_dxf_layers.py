import sys
import ezdxf
from glob import glob

def merge_layers(mapping_dict_for_merge, dxf_file_path):
    try:
        doc = ezdxf.readfile(dxf_file_path)
    except IOError:
        print(f"Not a DXF file or a generic I/O error.")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f"Invalid or corrupted DXF file.")
        sys.exit(2)
    # iterate over all entities in modelspace
    msp = doc.modelspace()
    counts = {k: 0 for k, v in mapping_dict_for_merge.items()}
    for e in msp:
        if e.dxf.layer in mapping_dict_for_merge.keys():
            counts[e.dxf.layer] += 1
            e.dxf.layer = mapping_dict_for_merge[e.dxf.layer]

    output_path = dxf_file_path.replace(".dxf", "_merged.dxf")
    doc.saveas(output_path)
    print("Merged layers -> ", counts, "-> ", output_path)


if __name__ == "__main__":
    files = glob("/media/hamzawl/Flux/Data/PowerLinesData/20240209SwissGrid2/03_Daten_Los_West_2024/*.dxf")
    for f in files:
        merge_layers({"Ketten": "Masten"}, f)
