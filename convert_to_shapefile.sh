#!/bin/sh

# Convert all input files from GeoJSON to ESRI Shapefile using ogr2ogr
for input in "$@"; do
	target=${input/json/shp}
	ogr2ogr -f "ESRI Shapefile" $target $input
done
