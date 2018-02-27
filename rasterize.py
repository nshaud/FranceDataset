import fiona
import rasterio
import rasterio.features
import pyproj
import geopandas as gpd
from shapely.geometry import Polygon

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
	
rasters = ["../BDORTHO_libre/BDORTHO_2-0_RVB-0M50_JP2-E080_LAMB93_D006_2014-01-01/BDORTHO/1_DONNEES_LIVRAISON_2017-09-00107/BDO_RVB_0M50_JP2-E080_LAMB93_D06-2014/06-2014-1035-6300-LA93-0M50-E080.jp2"]
rasters = rasters + rasters

shapefile = gpd.read_file('../Urban_Atlas2012/FR205L2_NICE/Shapefiles/FR205L2_NICE_UA2012.shp')

for raster in rasters:
	# Load raster image
	raster = rasterio.open(raster)
	print(shapefile.crs)
	print(raster.crs)
	if shapefile.crs != raster.crs:
		print("Reproject")
		shapefile = shapefile.to_crs(raster.crs)
	clipped_shapes = crop_shapefile_to_raster(shapefile, raster)
	shapes = ((geometry, UA_codes[item]) for geometry, item in zip(clipped_shapes.geometry, clipped_shapes['CODE2012']))
	meta = raster.meta.copy()
	# Use only one channel
	meta.update(count=1)
	burn_shapes(shapes, 'test.tif', meta)
