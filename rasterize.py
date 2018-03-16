import fiona
import fiona.crs
import rasterio
import rasterio.features
import pyproj
import geopandas as gpd
import shapely.geometry
from shapely.geometry import Polygon
import os
import argparse
from tqdm import tqdm
import datetime
import pyproj
from functools import partial


parser = argparse.ArgumentParser(description="Rasterize shapefiles based on an image mosaic")
parser.add_argument('tiles', metavar='tiles', type=str, nargs='+', help="Raster files")
parser.add_argument('--shapefiles', type=str, nargs='+', help="Shapefiles to use")
parser.add_argument('--dataset', type=str, help="'UA2012' or 'UA2006' for UrbanAtlas or 'cadastre'")
parser.add_argument('--dry', type=bool, const=True, nargs='?', help="Use to force a dry run (nothing is written).")
parser.add_argument('--skip', type=bool, const=True, nargs='?', help="Use to skip existing rasters and avoid re-writing (useful to resume an aborted job).")
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
	"""
	    Intersects of a GeoDataFrame with a raster

	    This creates the intersection between a Geopandas shapefile and a
	    rasterio raster. It returns a new shapefile containing only the polygons
	    resulting from this intersection.

	    :param shapefile: reference GeoDataFrame
	    :param raster: RasterIO raster object
	    :return: a GeoDataFrame containing the intersected polygons
	"""
	xmin, ymin, xmax, ymax = raster.bounds
	xmin_s, ymin_s, xmax_s, ymax_s = shapefile.total_bounds
	bounds_shp = Polygon( [(xmin_s,ymin_s), (xmin_s, ymax_s), (xmax_s, ymax_s), (xmax_s, ymin_s)] )
	bounds_raster = Polygon( [(xmin,ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)] )
	if bounds_shp.intersects(bounds_raster):
		# Compute the intersection of the bounds with the shapes
		shapefile['geometry'] = shapefile['geometry'].intersection(bounds_raster)
		# Filter empty shapes
		shapes_cropped = shapefile[shapefile.geometry.area>0]
		return shapes_cropped
	else:
		return None


def burn_shapes(shapes, destination, meta):
	"""
	    Writes a list of shapes and values in a raster

	    For each (polygon, value) in shapes, this burns the value in the
	    specified raster based on the polygon. Additionnal raster parameters
	    can be controlled with the meta dictionary.

	    :param shapes: list of (polygon, value) tuples
	    :param destination: string containing the path to the raster
	    :param meta: meta dictionary for raster management (RasterIO format)
	"""
	with rasterio.open(destination, 'w', **meta) as out:
		out_arr = out.read(1)
		burned = rasterio.features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform)
		out.write_band(1, burned)

def get_shapes(clipped_shapes, mode=None):
	"""
	    Extract a list of (polygon, value) tuples using specific dataset rules
	    from a GeoDataFrame.

	    :param clipped_shapes: GeoDataFrame to be processed
	    :param mode: dataset name ('UA2012', 'cadastre')
	    :return: a list of (polygon, value) tuples
	"""
	if mode == 'UA2012':
		shapes = [(geometry, UA2012_codes[item]) for geometry, item in zip(clipped_shapes.geometry, clipped_shapes['CODE2012'])]
	elif mode == 'cadastre':
		shapes = [(geometry, 255) for geometry in clipped_shapes.geometry]
	else:
		raise ValueError('Not implemented: {}.'.format(mode))
	return shapes

def reproject(shapefile, crs):
	"""
	    Reproject a shapefile to a specific CoordinateReferenceSystem

	    :param shapefile: a GeoDataFrame
	    :param crs: CoordinateReferenceSystem
	    :return: the projected GeoDataFrame
	"""
	return shapefile.to_crs(crs) if shapefile.crs != crs else shapefile

def clip_and_burn(shapefiles, raster, destination, skip_existing=False, filters=None):
	"""
	    Rasterize several shapefiles on a specific raster

	    This burns the objects contained in the shapefiles based on the raster
	    extent into a new raster.

	    :param shapefiles: a list of GeoDataFrame objects
	    :param raster: a RasterIO raster object
	    :param destination: path to the raster to write
	    :param skip_existing: set to True to avoid re-writing on existing rasters
	"""
	if skip_existing and os.path.exists(destination):
		return
	#tqdm.write("Clipping...")
	shapes = []
	for shapefile in shapefiles:
		bbox = project_bbox(raster.crs, shapefile.crs, raster.bounds)
		shp_crs = shapefile.crs
		s = (s[1] for s in shapefile.items(bbox=bbox))
		s = list(filter_shapefile(s, **filters))
		tqdm.write("{} objects in raster".format(len(s)))
		shapefile = gpd.GeoDataFrame.from_features(s, crs=shp_crs)
		if shapefile.empty:
			continue

		if shapefile.crs != raster.crs:
			#tqdm.write("Unknown new CRS: {}".format(raster.crs.to_string()))
			shapefile = reproject(shapefile, raster.crs)
		clipped_shapes = crop_shapefile_to_raster(shapefile, raster)
		if clipped_shapes is not None:
			shapes += get_shapes(clipped_shapes, mode=args.dataset)
	if len(shapes) == 0:
		tqdm.write("Skipping: raster does not intersect with shapefile")
	else:
		meta = raster.meta.copy()
		# Use only one channel
		meta.update(count=1, driver='GTiff', compress='lzw', dtype=rasterio.uint8)
		#tqdm.write("Saving to {}".format(destination))
		burn_shapes(shapes, destination, meta)

def str_to_date(date):
	"""
		Fast conversion between 'YYYY-mm-dd' string to Python date

		:param date: 'YYYY-mm-dd' string
		:return: Python datetime.date object
	"""
	return datetime.date(*map(int, date.split('-')))

def filter_shapefile(shapefile, end_date=None, clean=True):
	"""
	    This filters out objects from a shapefile based on pre-defined rules.

	    :param shapefile: a Fiona Collection shapefile
	    :param end_date: drops all objects with a 'creation_date' after this value
			     (default is None)
	    :return: the filtered GeoDataFrame
	"""

	if end_date is not None:
		end_date = str_to_date(end_date)
	
	def clean_func(shp):
		shape = shapely.geometry.shape(shp['geometry'])
		if not shape.is_valid:
			shp['geometry'] = shapely.geometry.mapping(shape.buffer(0))
		return shp

	def filter_date_func(shp):
		return str_to_date(shp['properties']['created']) < end_date

	if end_date is not None:
		shapefile = filter(filter_date_func, shapefile)
	shapefile = map(clean_func, shapefile)
	return shapefile

def clean(shapefile):
	"""
	    Cleans invalid polygons from the shapefile.

	    This works by adding a 0-width buffer to force invalid polygons
	    to be valid again in the shapefile.

	    :param shapefile: a GeoDataFrame
	    :return: a clean GeoDataFrame
	"""
	shapefile['geometry'] = shapefile.buffer(0)
	return shapefile

def project_bbox(crs_in, crs_out, bounds):
	"""
	    Project a bounding box from a CRS to another

	    :param crs_in: an input CoordinateReferenceSystem
	    :param crs_out: the target CoordinateReferenceSystem
	    :param bounds: a tuple of bounds (xmin, ymin, xmax, ymax)
	    :param return: the tuple of projected bounds
	"""
	xmin, ymin, xmax, ymax = bounds
	bbox = [(xmin,ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]
	transform = partial(pyproj.transform, pyproj.Proj(crs_in), pyproj.Proj(crs_out))
	new_coords = []
	for x1, y1 in bbox:
		x2, y2 = transform(x1, y1)
		new_coords.append((x2, y2))
	return Polygon(new_coords).bounds

def rasterize(args):
	rasters = args.tiles
	shapefiles = [fiona.open(shp) for shp in args.shapefiles]
	filters = {'end_date': args.end_date, 'clean': True}

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
				clip_and_burn(shapefiles, raster, destination, skip_existing=args.skip, filters=filters)


if __name__ == '__main__':
	args = parser.parse_args()
	rasterize(args)
