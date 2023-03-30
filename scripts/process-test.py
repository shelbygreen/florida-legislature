# import libraries
import os
import sys
import json
import glob
import subprocess
import us
import geopandas as gpd
from pathlib import Path

IN = Path("../data/geospatial/fetch")
OUT = Path("../data/geospatial/process")

# import openstates_metadata as metadata
def shp_to_geojson(geojson_path, is_state_file):
    # read in the shp and store it in a geodataframe
    gdf = gpd.read_file(geojson_path)

    # add bounds
    # gdf['bounds'] = gdf.bounds.round(2).apply(lambda row: list(row), axis=1)

    chamber = "House" if geojson_path.stem.endswith("sldl") else "Senate"

    # parse to geojson
    gdf_parsed = gdf.to_json()
    geojson = json.loads(gdf_parsed)

    # add fields to each feature -- geoid, bounds, state abbr, chamber, district
    for feature in geojson["features"]:
        # rename keys in state files
        if is_state_file:
            for key in [k for k in feature["properties"].keys()]:
                new_key = key.replace("10", "")
                feature["properties"][new_key] = feature["properties"].pop(key)

        state = us.states.lookup(feature["properties"]["STATEFP"])
        print(state)
        geoid = feature["properties"]["GEOID"]
        # bounds = feature["properties"]["bounds"]

        if is_state_file:
            name = state.name
            ccid = state.fips
        else:
            name = (
                us.states.lookup(feature["properties"]["STATEFP"]).name
                + " "
                + feature["properties"]["NAMELSAD"]
            )

            # create new features
            ccid = (
                feature["properties"]["GEOID"] + "U"
                if feature["properties"]["LSAD"] == "LU"
                else feature["properties"]["GEOID"] + "L"
            )

            district = (
                feature["properties"]["SLDLST"].lstrip("0")
                if "SLDLST" in feature["properties"].keys()
                else feature["properties"]["SLDUST"].lstrip("0")
            )

        feature["properties"] = {
            "state_fips": state.fips,
            "state_abbr": state.abbr,
            "geoid": geoid,
            "ccid": ccid,
            "name": name,
            # "bounds": bounds,
        }

        if not is_state_file:
            feature["properties"]["chamber"] = chamber
            feature["properties"]["district"] = district
        else:
            # if the shape is a state, and the shape is included in the final
            # shapefile, then we have no data on that state, and we want the
            # entire state to have a flag value for cc_score
            feature["properties"]["cc_score"] = 999

    # export to geojson file
    region_type = "state" if is_state_file else chamber.lower()
    output_path = OUT / f"{state.abbr}-{region_type}.geojson"
    print(f" {state.abbr}-{region_type} shp => {output_path.name}")

    # if the output directory doesn't exist, create it
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True)

    with open(output_path, "w+") as geojson_file:
        json.dump(geojson, geojson_file)
        
files = sorted(IN.glob("tl*.shp"))

# convert from shp to geojson
for file in files:
    is_state_file = "state10" in file.name

    # create geojson in source folder
    newfilename = file.with_suffix(".geojson")
    if os.path.exists(newfilename):
        print(newfilename, "already exists, skipping")
    else:
        print(file, "=>", newfilename)
        subprocess.run(
            [
                "ogr2ogr",
                "-where",
                f"GEOID{'10' if is_state_file else ''} NOT LIKE '%ZZZ'",
                "-t_srs",
                "crs:84",
                "-f",
                "GeoJSON",
                newfilename,
                file,
            ],
            check=True,
        )
    # create geojson in all folder
    shp_to_geojson(newfilename, is_state_file)

# finished message
print("Done converting shp to geojson")