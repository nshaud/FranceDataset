import fiona
import rasterio
import rasterio.features
import pyproj
import geopandas as gpd
from shapely.geometry import Polygon
import os
import argparse


parser = argparse.ArgumentParser(description="Rasterize shapefiles based on an image mosaic")
parser.add_argument('tiles', metavar='tiles', type=str, nargs='+', help="Raster files")
parser.add_argument('--shapefile', type=str, help="Shapefile to use")
parser.add_argument('--dataset', type=str, help="'UA' for UrbanAtlas or 'cadastre'")

args = parser.parse_args()

UA_codes = {'11100': 1,
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
 '92000': 29}


def crop_shapefile_to_raster(shapefile, raster):
	xmin, ymin, xmax, ymax = raster.bounds
	bounds = Polygon( [(xmin,ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)] )
	# Compute the intersection of the bounds with the shapes
	shapefile = shapefile.copy()
	shapefile['geometry'] = shapefile['geometry'].intersection(bounds)
	# Filter empty shapes
	shapes_cropped = shapefile[shapefile.geometry.area>0]
	return shapes_cropped


def burn_shapes(shapes, destination, meta):
	with rasterio.open(destination, 'w', **meta) as out:
		out_arr = out.read(1)
		burned = rasterio.features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform)
		out.write_band(1, burned)

def get_shapes(clipped_shapes, mode=None):
	if mode == 'UA':
		shapes = [(geometry, UA_codes[item]) for geometry, item in zip(clipped_shapes.geometry, clipped_shapes['CODE2012'])]
	elif mode == 'cadastre':
		shapes = [(geometry, 255) for geometry in clipped_shapes.geometry]
	else:
		raise ValueError('Not implemented: {}.'.format(mode))
	return shapes


if __name__ == '__main__':
	rasters = args.tiles
	shapefile = gpd.read_file(args.shapefile)

	for raster in rasters:
		filename, extension = os.path.splitext(raster)
		destination = "{}_{}.{}".format(filename, args.dataset, 'tif')
		# Load raster image
		raster = rasterio.open(raster)
		if shapefile.crs != raster.crs:
			print("Reproject shapefile to {}".format(raster.crs['init']))
			shapefile = shapefile.to_crs(raster.crs)
		clipped_shapes = crop_shapefile_to_raster(shapefile, raster)
		shapes = get_shapes(clipped_shapes, mode=args.dataset)
		if len(shapes) == 0:
			print("Skipping raster does not intersect with shapefile")
			continue
		meta = raster.meta.copy()
		# Use only one channel
		meta.update(count=1)
		print("Saving to {}".format(destination))
		burn_shapes(shapes, destination, meta)
