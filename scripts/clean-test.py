# import libraries
import json
import shutil
import geojson
import subprocess
from pathlib import Path
from shapely.geometry import shape, mapping, MultiPolygon

# a few states have Point features in their geojson shapes, we
# need to remove those for geojson-merge and mapshaper to able
# to handle them
POINTS_STATES = ["DE", "NJ", "LA", "MD", "NC", "OH", "PR", "MS"]


def remove_points(raw_dir, clean_dir, glob_ptrn):
    for raw_shape in sorted(raw_dir.glob(glob_ptrn)):
        state_abbr = raw_shape.stem.split("-")[0]

        print(f"{raw_shape} => {clean_dir / raw_shape.name}")

        if state_abbr in POINTS_STATES:
            state_json = json.load(open(raw_shape, "r"))

            for feature in state_json["features"]:
                if feature["geometry"]["type"] == "GeometryCollection":
                    polys = [
                        shape(geom)
                        for geom in feature["geometry"]["geometries"]
                        if geom["type"] in ["Polygon", "MultiPolygon"]
                    ]
                    feature["geometry"] = json.loads(
                        json.dumps(mapping(MultiPolygon(polys)))
                    )

            with open(clean_dir / raw_shape.name, "w") as f:
                json.dump(state_json, open(clean_dir / raw_shape.name, "w"))
        else:
            shutil.copy(raw_shape, clean_dir / raw_shape.name)


def clip_chamber_shapes(raw_dir, clean_dir, glob_ptrn):
    for raw_shape in sorted(raw_dir.glob(glob_ptrn)):
        clean_shape = clean_dir / raw_shape.name

        if clean_shape.exists():
            print(f"{clean_shape} exists, skipping")
            continue

        print(f"{raw_shape} => {clean_shape}")
        subprocess.run(
            [
                "ogr2ogr",
                "-clipsrc",
                "../data/geospatial/fetch/cb_2021_us_nation_5m.shp",
                str(clean_shape),
                str(raw_shape),
            ],
            check=True,
        )


def reproject_chamber_shapes(raw_dir, clean_dir):
    for raw_shape in sorted(raw_dir.glob("*.geojson")):
        clean_shape = clean_dir / raw_shape.name

        if clean_shape.exists():
            print(f"{clean_shape} exists, skipping")
            continue

        print(f"{raw_shape} => {clean_shape}")
        subprocess.run(
            [
                "cat "
                + str(raw_shape)
                + " | dirty-reproject --forward albersUsa > "
                + str(clean_shape)
            ],
            shell=True,
        )

        # TEMP(matt): for some reason, reprojecting in some state chambers
        # makes the geojson invalid. This might be a problem with dirty-reproject,
        # a workaround for now is to make sure the geojson came out valid, and
        # re-export via mapshaper if not
        if not geojson.load(open(clean_shape, "r")).is_valid:
            shape_to_fix = clean_shape.rename(
                clean_shape.with_name(f"{clean_shape.stem}-temp{clean_shape.suffix}")
            )

            subprocess.run(
                [
                    "mapshaper "
                    + str(shape_to_fix)
                    + f" -o {str(clean_dir / raw_shape.name)}"
                ],
                shell=True,
            )

            shape_to_fix.unlink()


if __name__ == "__main__":
    print("Downloading national boundary")

    # MANUAL
    # subprocess.run(
    #     "curl --silent --output ../data/geospatial/fetch/cb_2020_us_nation_5m.zip"
    #     "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_nation_5m.zip".split()
    # )
    # subprocess.run(
    #     "unzip -q -o -d ../data/geospatial/fetch"
    #     "../data/geospatial/fetch/cb_2020_us_nation_5m.zip".split()
    # )

    print("Clip GeoJSON to shoreline & reproject")
    # for house files
    raw_shapes = Path("../data/geospatial/process")
    clipped_shapes = Path("../data/geospatial/clipped")
    depointed_shapes = Path("../data/geospatial/depointed")
    clean_shapes = Path("../data/geospatial/clean")

    for output in [
        clipped_shapes / "house",
        clipped_shapes / "senate",
        clipped_shapes / "state",
        depointed_shapes / "house",
        depointed_shapes / "senate",
        depointed_shapes / "state",
        clean_shapes / "house",
        clean_shapes / "senate",
        clean_shapes / "state",
    ]:
        output.mkdir(parents=True, exist_ok=True)

    # handle states
    # clip_chamber_shapes(raw_shapes, clipped_shapes / "state", "*state.geojson")
    # remove_points(
    #     clipped_shapes / "state", depointed_shapes / "state", "*state.geojson"
    # )
    # reproject_chamber_shapes(depointed_shapes / "state", clean_shapes / "state")
    # reproject_chamber_shapes(clipped_shapes / "state", clean_shapes / "state")

    # handle house
#     clip_chamber_shapes(raw_shapes, clipped_shapes / "house", "*house.geojson")
    # remove_points(
    #     clipped_shapes / "house", depointed_shapes / "house", "*house.geojson"
    # )
    # reproject_chamber_shapes(depointed_shapes / "house", clean_shapes / "house")
    # reproject_chamber_shapes(clipped_shapes / "house", clean_shapes / "house")


    # handle senate
    clip_chamber_shapes(raw_shapes, clipped_shapes / "senate", "*senate.geojson")
    remove_points(
        clipped_shapes / "senate", depointed_shapes / "senate", "*senate.geojson"
    )
    reproject_chamber_shapes(depointed_shapes / "senate", clean_shapes / "senate")
    reproject_chamber_shapes(clipped_shapes / "senate", clean_shapes / "senate")


    # remove the intermediate files
    shutil.rmtree(clipped_shapes)
#     shutil.rmtree(depointed_shapes)

    print("Done reprojecting. Check the clean folder for results")