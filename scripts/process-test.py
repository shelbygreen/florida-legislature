# import libraries
import os
import sys
import json
import glob
import subprocess
import us
import geopandas as gpd
from pathlib import Path

# name the IN and OUT path
# in - fetch folder
# out - process folder

IN = Path("../data/geospatial/fetch")
OUT = Path("../data/geospatial/process")

# function to convert shapefile into geojson file
def shp_to_geojson(geojson_path):
    
    # read in the shp file and store it in a geodataframe
    gdf = gpd.read_file(geojson_path)

    # add 'chamber' field
    # if the file name ends in "sldl", set chamber as House
    # if not, set chamber as Senate
    chamber = "House" if geojson_path.stem.endswith("sldl") else "Senate"
    
    # parse to geojson
    gdf_parsed = gdf.to_json()
    geojson = json.loads(gdf_parsed)
    
    print("checkpoint 3 - modifying the features of the geojson file")

    # add fields to each feature
    # new features: geoid, ccid, state abbr, chamber, district, name
    for feature in geojson["features"]:
        
        # add state field
        state = us.states.lookup('12')
        
        # add 'GEOID' field
        GEOID = '12' + str(feature["properties"]["DISTRICT"]).zfill(3)
        
        # add district field
        district = (
            feature["properties"]["DISTRICT"]
        )

        # add name field
        name = (
            us.states.lookup('12').name
            + " State "
            + chamber
            + " "
            + str(district)
        )
        
        # add ccid field
        ccid = (
            GEOID + "U"
            if chamber == "Senate"
            else GEOID + "L"
        )

        # all features
        feature["properties"] = {
            "state_fips": state.fips,
            "state_abbr": state.abbr,
            "geoid": GEOID,
            "ccid": ccid,
            "name": name,
            "chamber": chamber,
            "district": district,
            "population":feature["properties"]["TOTAL"]
        }


    # export to geojson file
    region_type = chamber.lower()
    output_path = OUT / f"{state.abbr}-{region_type}.geojson"
    print(f" {state.abbr}-{region_type} shp => {output_path.name}")

    # if the output directory doesn't exist, create it
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True)

    with open(output_path, "w+") as geojson_file:
        json.dump(geojson, geojson_file)
        
# create list of files
# from fetch folder, starting with FL
files = sorted(IN.glob("FL*.shp"))
print("checkpoint 1 - create list of shp files in fetch folder")

# convert from shp to geojson
for file in files:
    print("checkpoint 2 - {0} being converted".format(file))

    # create geojson in source folder
    newfilename = file.with_suffix(".geojson")
    if os.path.exists(newfilename):
        print(newfilename, "already exists, skipping")
    else:
        print(file, "=>", newfilename)
        subprocess.run(
            [
                "ogr2ogr",
                "-t_srs",
                "crs:84",
                "-f",
                "GeoJSON",
                newfilename,
                file,
            ],
            check=True,
        )
    # create geojson in fetch & process folder
    shp_to_geojson(newfilename)

# finished message
print("Done converting shp to geojson")