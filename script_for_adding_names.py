import os.path
import typing
import warnings
import xml.etree.ElementTree as ET
from typing import Dict, Any
import pandas as pd
import numpy as np
from pyproj import CRS, Transformer
from namak.GeoUtils import GeoToCartesianMeters, CylindricalCoordinatesToGeo
from namak.helper import checkmkdir
import json

import simplifyTowerStructure


def convert_coordinates(x: float, y: float, height: float = None):
    # Define the Coordinate Reference Systems
    src_crs = CRS("EPSG:21781")  # CH1903+ / LV95
    dest_crs = CRS("EPSG:4326")  # WGS84

    # Initialize the transformer
    transformer = Transformer.from_crs(src_crs, dest_crs)

    # Transform the coordinates
    lon, lat = transformer.transform(x, y)
    return [lon, lat] if height is None else [lon, lat, height]


def build_dict(xml_file: str):
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
                            float(y_elem.text),
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

                structure_dict[struct_number_elem.text]["mid_span_points"].append(
                    convert_coordinates(
                        float(struct_report.find('mid_span_point_x').text),
                        float(struct_report.find('mid_span_point_x').text),
                        float(struct_report.find('mid_span_point_x').text),
                    ))

                structure_dict[struct_number_elem.text]["name"].append(struct_report.find('set_label').text)

    # for tower in structure_dict.keys():
    #     for coordinate_name in structure_dict[tower]:
    #         if coordinate_name != "name":
    #             structure_dict[tower][coordinate_name] = convert_coordinates(*structure_dict[tower][coordinate_name])

    return structure_dict


# Usage:


def get_geojson(file_path):
    # Read GeoJSON file
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def write_geojson(file_path, geojson):
    # Write GeoJSON file
    with open(file_path, 'w') as f:
        json.dump(geojson, f, indent="\t")


def get_geo_coordinates_poi(feature, index):
    poi = feature["properties"]["pois"][index]


def add_names(json_dict: dict, xml_dict: dict) -> dict:
    # vectorizedFn = np.vectorize(GeoToCartesianMeters)

    towers_in_json: int = sum(
        [1 for feature in json_dict["features"] if feature["properties"]["type"] == "electric_pole"])
    towers_in_xml: int = len(xml_dict)

    # solve this issue! get from gil and check
    if towers_in_json != towers_in_xml:
        warnings.warn(f"Incorrect matching for number of towers -> xml: {towers_in_xml} vs json -> {towers_in_json}")

    xml_names = [key for key in xml_dict.keys()]
    xml_coordinates = np.array([xml_dict[key]["coordinates"][:2] for key in xml_dict.keys()])

    tower_association_deltas = []
    skipped_towers = 0
    for feature in json_dict["features"]:
        if feature["properties"]["type"] == "electric_pole":

            # add tower name
            json_coords = feature["geometry"]["coordinates"][::-1]
            distances = np.linalg.norm([
                GeoToCartesianMeters(json_coords, xml_coord) for xml_coord in xml_coordinates],
                                       axis=1)
            min_index = np.argmin(distances)

            if distances[min_index] < 10:
                feature["properties"]["name"] = xml_names[min_index]
                feature["properties"]["terrain"] = "1670"

                tower_association_deltas.append(distances[min_index])
                # add poi names
                pois_xml = xml_dict[xml_names[min_index]]["insulator_attach_points"]
                print(f"Compare_pois -> {len(pois_xml)} vs {len(feature['properties']['pois']) - 1}")

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
                #
                # remove tower from xml_coordinates
                xml_coordinates = np.delete(xml_coordinates, min_index, 0)
                xml_names.pop(min_index)
            else:
                print(f"No tower found for coordinates: {feature['properties']['name']}: {json_coords} | {distances[min_index]}")
                skipped_towers += 1
    print(f"Missing towers {xml_names}")
    print(
        f"Matching towers {len(tower_association_deltas)}\n"
        f"max delta {np.max(tower_association_deltas)}\n"
        f"skipped towers from json {skipped_towers}\n"
        f"xml towers {towers_in_xml}\n"
        f"json towers {towers_in_json}")
    return json_dict

def get_dataframe_for_single_tower(tower: typing.Dict) -> pd.DataFrame:
    tower_dataframe: pd.DataFrame = pd.DataFrame()
    tower_name = tower["properties"]["name"]
    tower_base_asl_meters = tower["properties"]["poleBaseASLMeters"]
    tower_base_lat_long = tower["geometry"]["coordinates"][::-1]
    for poi in tower["properties"]["pois"]:
        poi_dict: Dict[str,  Any] = {}
        poi_dict["tower_name"] = [tower_name]
        geo = CylindricalCoordinatesToGeo(tower_base_lat_long, poi["distance"], poi["azimuth"], None)

        poi_dict["latitude"] = [geo[0]]
        poi_dict["longitude"] = [geo[1]]
        poi_dict["height"] = [poi["height"] + tower_base_asl_meters]
        poi_dict["isCalibration"] = [1 if poi["type"] == "CALIBRATION" else 0]

        tower_dataframe = pd.concat([tower_dataframe, pd.DataFrame(poi_dict)])
    return tower_dataframe

def get_dataframe_of_pois_from_json_site(json: typing.Dict):
    totalDataFrame: pd.DataFrame = pd.DataFrame()
    for feature in json["features"]:
        if feature["properties"]["type"] == "electric_pole":
            df = get_dataframe_for_single_tower(feature)
            totalDataFrame = pd.concat([totalDataFrame, df])
    return totalDataFrame

if __name__ == "__main__":
    file_path = '/mnt/00A03D3C0BCCF8D8/Data/PowerLinesData/20230517SwissGridComplete/Los_West/TR1711_Chamoson-Chippis_LV03/TR1711.json'
    json_dict: dict = get_geojson(file_path)
    xml_file = '/mnt/00A03D3C0BCCF8D8/Data/PowerLinesData/20230517SwissGridComplete/Los_West/TR1711_Chamoson-Chippis_LV03/TR1711_Chamoson-Chippis.xml'
    xml_dict: dict = build_dict(xml_file)


    xml_dict = dict(filter(lambda x: x[0][:5] == '1711x', xml_dict.items()))

    json_dict2: dict = add_names(json_dict, xml_dict)

    json_dict2 = simplifyTowerStructure.simplifyTowerstruct(json_dict2)

    folder_name = os.path.join(os.path.split(file_path)[0], "processed")
    checkmkdir(folder_name)
    file_name = os.path.basename(file_path)
    writing_path: str = os.path.join(folder_name, os.path.splitext(file_name)[0] + "_processed")
    write_geojson(
        writing_path + ".json",
        json_dict2)

    if True:
        dataframe_of_pois = get_dataframe_of_pois_from_json_site(json_dict2)
        dataframe_of_pois.to_csv(
            writing_path + ".csv"
        )
