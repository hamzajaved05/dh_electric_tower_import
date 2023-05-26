import xml.etree.ElementTree as ET
from nmk.GeoUtils import CHtoWGS84
import numpy as np
from pyproj import CRS, Transformer
from nmk.GeoUtils import GeoToCartesianMeters
from tower.pointofinterest import POI

def convert_coordinates(x, y, height=None):
    # Define the Coordinate Reference Systems
    src_crs = CRS("EPSG:2056")  # CH1903+ / LV95
    dest_crs = CRS("EPSG:4326")  # WGS84

    # Initialize the transformer
    transformer = Transformer.from_crs(src_crs, dest_crs)

    # Transform the coordinates
    lon, lat = transformer.transform(x, y)
    return [lon, lat] if height is None else [lon, lat, height]

def build_dict(xml_file):
    # Initialize the dictionary
    structure_dict = {}

    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find 'Structure Coordinates Report' table
    for table in root.iter('table'):
        if table.attrib.get('plsname', '') == 'Structure Coordinates Report':
            # Iterate over structure_coordinates_report elements in the table
            for struct_report in table.iter('structure_coordinates_report'):
                # Look for 'struct_number' and 'x' tags
                struct_number_elem = struct_report.find('struct_number')
                x_elem = struct_report.find('x')
                y_elem = struct_report.find('y')
                z_elem = struct_report.find('z')

                if struct_number_elem is not None and x_elem is not None and y_elem is not None and z_elem is not None:
                    # Add to dictionary as a tuple (value, units)
                    structure_dict[struct_number_elem.text] = {"coordinates": 
                        convert_coordinates(
                        float(x_elem.text),
                        float( y_elem.text), 
                        float(z_elem.text))
                       }
                structure_dict[struct_number_elem.text]["insulator_attach_points"] = []
                structure_dict[struct_number_elem.text]["wire_attach_points"] = []
                structure_dict[struct_number_elem.text]["name"] = []
    
    
    for table in root.iter('table'):
        if table.attrib.get('plsname', '') == 'Structure Attachment Coordinates':
            for struct_report in table.iter('structure_attachment_coordinates'):
                struct_number_elem = struct_report.find('struct_number')
                structure_dict[struct_number_elem.text]["insulator_attach_points"].append(
                    convert_coordinates(
                    float(struct_report.find('insulator_attach_point_x').text),
                    float(struct_report.find('insulator_attach_point_y').text),
                    float(struct_report.find('insulator_attach_point_z').text),
                ))

                structure_dict[struct_number_elem.text]["wire_attach_points"].append(
                    convert_coordinates(
                    float(struct_report.find('wire_attach_point_x').text),
                    float(struct_report.find('wire_attach_point_y').text),
                    float(struct_report.find('wire_attach_point_z').text),
                ))

                structure_dict[struct_number_elem.text]["name"].append(struct_report.find('set_label').text)

    # for tower in structure_dict.keys():
    #     for coordinate_name in structure_dict[tower]:
    #         if coordinate_name != "name":
    #             structure_dict[tower][coordinate_name] = convert_coordinates(*structure_dict[tower][coordinate_name])

    return structure_dict


# Usage:
xml_file = '/mnt/00A03D3C0BCCF8D8/Data/PowerLinesData/20230508SwissGrid/testLine/TR1670_Riddes-Avise_Valpeline_IT/TR1670_Riddes-Avise_Valpeline_IT.xml'
xml_dict = build_dict(xml_file)

import json

def get_geojson(file_path):
    # Read GeoJSON file
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def writ_geojson(file_path, geojson):
    # Write GeoJSON file
    with open(file_path, 'w') as f:
        json.dump(geojson, f, indent = "\t")

file_path = '/mnt/00A03D3C0BCCF8D8/Data/PowerLinesData/20230508SwissGrid/testLine/TR1670_Riddes-Avise_Valpeline_IT/TR1670_Riddes-Avise_Valpeline_IT_raw.json'
json_dict = get_geojson(file_path)

def getGeoCoordinatesPoi(feature, index):
    poi =  feature["properties"]["pois"][index]

def add_names(json_dict, xml_dict):
    # vectorizedFn = np.vectorize(GeoToCartesianMeters)
    xml_names = [key for key in xml_dict.keys()]
    xml_coordinates = np.array([xml_dict[key]["coordinates"][:2] for key in xml_dict.keys()])

    for feature in json_dict["features"]:
        if feature["properties"]["type"] == "electric_pole":

            # add tower name
            json_coords = feature["geometry"]["coordinates"][::-1]
            distances = np.linalg.norm([GeoToCartesianMeters(json_coords, xml_coord) for xml_coord in xml_coordinates], axis=1)
            min_index = np.argmin(distances)

            if distances[min_index] < 1e-3:
                feature["properties"]["name"] = xml_names[min_index]
                print("Tower found for coordinates: {}: {}".format(feature["properties"]["name"], distances[min_index]))


                # add poi names
                # pois_xml = xml_dict[xml_names[min_index]]["insulator_attach_points"]
                # print(f"Compare_pois -> {len(pois_xml)} vs {len(feature['properties']['pois']) - 1}")

                # used = set()
                # for i in range(1, len(feature["properties"]["pois"])):
                #     poi = feature["properties"]["pois"][i]
                #     asl = feature["properties"]["poleBaseASLMeters"]
                #     towerBaseLatLon = feature["geometry"]["coordinates"][::-1]
                #     coords = POI(poi["height"], poi["distance"], poi["azimuth"]).get_lat_lon(towerBaseLatLon, asl = asl)
                #     distances = np.linalg.norm([GeoToCartesianMeters(coords, xml_coord) for xml_coord in pois_xml], axis=1)
                #     min_index_poi = np.argmin(distances)
                    
                #     if distances[min_index_poi] > 1.5:
                #         continue

                #     if min_index_poi in used:
                #         raise Exception("POI already used")
                #     used.add(min_index_poi)
                #     feature["properties"]["pois"][i]["name"] = xml_dict[xml_names[min_index]]["name"][min_index_poi]

                # remove tower from xml_coordinates
                xml_coordinates = np.delete(xml_coordinates, min_index, 0)
                xml_names.pop(min_index)
            else:
                print("No tower found for coordinates: {}: {}".format(feature["properties"]["name"], json_coords))

    return json_dict

json_dict2 = add_names(json_dict, xml_dict)
writ_geojson('/mnt/00A03D3C0BCCF8D8/Data/PowerLinesData/20230508SwissGrid/testLine/TR1670_Riddes-Avise_Valpeline_IT/TR1670_Riddes-Avise_Valpeline_IT.json', json_dict2)
print(json_dict)