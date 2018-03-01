import subprocess
import argparse
import os

try:
    from joblib import Parallel, delayed
    JOBLIB = True
except ImportError:
    JOBLIB = False

parser = argparse.ArgumentParser(description="Convert GeoJSON files to ESRI Shapefiles using ogr2ogr.")
parser.add_argument('files', metavar='JSON files', nargs='+', help="GeoJSON files to be converted")
parser.add_argument('--jobs', type=int, default=1, help="Number of parallel jobs to run")

def convert_filename(geojson_file):
    filename, ext = os.path.splitext(geojson_file)
    return "{}.shp".format(filename)

def run_conversion(shapefile, geojson_file):
    command = ["ogr2ogr", '-f', 'ESRI Shapefile', shapefile, geojson_file ]
    print("Running {}".format(" ".join(command)))
    subprocess.run(command)

if __name__ == '__main__':
    args = parser.parse_args()
    # Check if joblib is available
    if args.jobs > 1 and not JOBLIB:
        print("Warning: joblib is not available. Sequential processing only.")
        args.jobs = 1


    shapefiles = map(convert_filename, args.files)

    if JOBLIB:
        Parallel(n_jobs=args.jobs)(delayed(run_conversion) (s, g) for s, g in zip(shapefiles, args.files))
    else:
        for geojson_file, shapefile in zip(args.files, shapefiles):
            run_conversion(shapefile, geojson_file)
