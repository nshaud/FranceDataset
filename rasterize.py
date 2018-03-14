import fiona
import fiona.crs
import rasterio
import rasterio.features
import pyproj
import geopandas as gpd
from shapely.geometry import Polygon
import os
import argparse
from tqdm import tqdm
import datetime

parser = argparse.ArgumentParser(description="Rasterize shapefiles based on an image mosaic")
parser.add_argument('tiles', metavar='tiles', type=str, nargs='+', help="Raster files")
parser.add_argument('--shapefiles', type=str, nargs='+', help="Shapefiles to use")
parser.add_argument('--dataset', type=str, help="'UA2012' or 'UA2006' for UrbanAtlas or 'cadastre'")
parser.add_argument('--dry', type=bool, const=True, nargs='?', help="Use to force a dry run (nothing is written).")
parser.add_argument('--end_date', type=str, default=None, nargs='?', help="For 'cadastre' dataset, remove all objects created after this date ('YYYY-mm-dd' format).")

UA2012_codes = {'11100': 1,
 '11210': 2,
 '11220': 3,
 '11230': 4,
 '11240': 5,
 '11300': 6,
 '12100': 7,
 '12210': 8,
 '12220': 9,
 '12230': 10,
 '12300': 11,
 '12400': 12,
 '13100': 13,
 '13300': 14,
 '13400': 15,
 '14100': 16,
 '14200': 17,
 '21000': 18,
 '22000': 19,
 '23000': 20,
 '24000': 21,
 '25000': 22,
 '31000': 23,
 '32000': 24,
 '33000': 25,
 '40000': 26,
 '50000': 27,
 '91000': 28,
 '92000': 29,
 '25400': 28,
 '25500': 29}

def crop_shapefile_to_raster(shapefile, raster):
	xmin, ymin, xmax, ymax = raster.bounds
	xmin_s, ymin_s, xmax_s, ymax_s = shapefile.total_bounds
	bounds_shp = Polygon( [(xmin_s,ymin_s), (xmin_s, ymax_s), (xmax_s, ymax_s), (xmax_s, ymin_s)] )
	bounds_raster = Polygon( [(xmin,ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)] )
	if bounds_shp.intersects(bounds_raster):
		# Compute the intersection of the bounds with the shapes
		shapefile = shapefile.copy()
		shapefile['geometry'] = shapefile['geometry'].intersection(bounds_raster)
		# Filter empty shapes
		shapes_cropped = shapefile[shapefile.geometry.area>0]
		return shapes_cropped
	else:
		return None


def burn_shapes(shapes, destination, meta):
	with rasterio.open(destination, 'w', **meta) as out:
		out_arr = out.read(1)
		burned = rasterio.features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform)
		out.write_band(1, burned)

def get_shapes(clipped_shapes, mode=None):
	if mode == 'UA2012':
		shapes = [(geometry, UA2012_codes[item]) for geometry, item in zip(clipped_shapes.geometry, clipped_shapes['CODE2012'])]
	elif mode == 'cadastre':
		shapes = [(geometry, 255) for geometry in clipped_shapes.geometry]
	else:
		raise ValueError('Not implemented: {}.'.format(mode))
	return shapes

def reproject(shapefile, crs):
	return shapefile.to_crs(crs) if shapefile.crs != crs else shapefile

def clip_and_burn(shapefiles, raster, destination):
	#tqdm.write("Clipping...")
	shapes = []
	for shapefile in shapefiles:
		if shapefile.crs != raster.crs:
			tqdm.write("Unknown new CRS: {}".format(raster.crs.to_string()))
			shapefile = reproject(shapefile, raster.crs)
		clipped_shapes = crop_shapefile_to_raster(shapefile, raster)
		if clipped_shapes is not None:
			shapes += get_shapes(clipped_shapes, mode=args.dataset)
	if len(shapes) == 0:
		tqdm.write("Skipping: raster does not intersect with shapefile")
	else:
		meta = raster.meta.copy()
		# Use only one channel
		meta.update(count=1)
		#tqdm.write("Saving to {}".format(destination))
		burn_shapes(shapes, destination, meta)

def filter_shapefile(shapefile, end_date=None):
	end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
	to_drop = []
	for i in range(len(shapefile)):
		created = shapefile.at[i, 'created']
		creation_date = datetime.datetime.strptime(created, '%Y-%m-%d')
		if creation_date > end_date:
			to_drop.append(i)
	tqdm.write("Filtered {} buildings over {}".format(len(to_drop), len(shapefile)))
	return shapefile.drop(to_drop)

if __name__ == '__main__':
	args = parser.parse_args()
	rasters = args.tiles
	shapefiles = [gpd.read_file(shp) for shp in tqdm(args.shapefiles, desc="Reading shapefiles...")]
	if args.end_date is not None:
		tqdm.write("Filtering all buildings created after {}".format(args.end_date))
		shapefiles = [filter_shapefile(s, end_date=args.end_date) for s in shapefiles]
	print("Done.")
	with rasterio.open(rasters[0]) as raster:
		# Load first raster image
		raster = rasterio.open(rasters[0])
		for idx, shapefile in enumerate(shapefiles):
			if raster.crs != shapefile.crs:
				print("Reproject shapefile from {} to {}.".format(fiona.crs.to_string(shapefile.crs), raster.crs.to_string()))
				shapefiles[idx] = reproject(shapefile, raster.crs)

	print("Start processing.")
	if args.dry:
		print("DRY RUN --- NOTHING WILL BE WRITTEN !")
	t_rasters = tqdm(rasters)
	for raster_file in t_rasters:
		t_rasters.set_description("Processing {}".format(os.path.basename(raster_file)))
		filename, extension = os.path.splitext(raster_file)
		destination = "{}_{}.{}".format(filename, args.dataset, 'tif')
		if not args.dry:
			with rasterio.open(raster_file) as raster:
				clip_and_burn(shapefiles, raster, destination)

