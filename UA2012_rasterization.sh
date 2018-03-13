# 06 - Alpes-Maritimes : NICE
python rasterize.py --shapefiles Urban_Atlas2012/FR205L2_NICE/Shapefiles/FR205L2_NICE_UA2012.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D006*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2 

# 13 - Bouches-du-Rhônes : MARSEILLE, MARTIGUES
python rasterize.py --shapefiles Urban_Atlas2012/FR*{MARSEILLE,MARTIGUES}/Shapefiles/FR*.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D013*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2

# 14 - Calvados : CAEN
python rasterize.py --shapefiles Urban_Atlas2012/FR*CAEN/Shapefiles/FR*.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D014*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2 

# 22 - Côte d'Armor : SAINT BRIEUC, RENNES
python rasterize.py --shapefiles Urban_Atlas2012/FR*RENNES/Shapefiles/FR*.shp Urban_Atlas2012/FR066L2_SAINT_BRIEUC/Shapefiles/FR066L2_SAINT_BRIEUC_UA2012.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D022*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2 

# 29 - Finistère : QUIMPER, BREST, LORIENT
python rasterize.py --shapefiles Urban_Atlas2012/FR*{LORIENT,QUIMPER,BREST}/Shapefiles/FR*.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D029*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2 

# 35 - Ille-et-Villaine : RENNES
python rasterize.py --shapefiles Urban_Atlas2012/FR*RENNES/Shapefiles/FR*.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D035*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2

# 44 - Loire-Atlantique : NANTES, SAINT-NAZAIRE
python rasterize.py --shapefiles Urban_Atlas2012/FR*{NANTES,NAZAIRE}/Shapefiles/FR*.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D044*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2

# 49 - Maine-et-Loire : ANGERS
python rasterize.py --shapefiles Urban_Atlas2012/FR*ANGERS/Shapefiles/FR*.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D049*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2 

# 50 - Manche : CHERBOURG
python rasterize.py --shapefiles Urban_Atlas2012/FR069L2_CHERBOURG/Shapefiles/FR069L2_CHERBOURG_UA2012.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D050*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2 

# 56 - Morbihan : VANNES, LORIENT, SAINT-NAZAIRE
python rasterize.py --shapefiles Urban_Atlas2012/FR*{VANNES,LORIENT,NAZAIRE}/Shapefiles/FR*.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D056*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2 

# 59 - Nord : DUNKERQUE, CALAIS, BOULOGNE-SUR-MER, LENS, ARRAS, HENIN, VALENCIENNES, DOUAI, LILLE
python rasterize.py --shapefiles Urban_Atlas2012/FR*{DUNKERQUE,CALAIS,LILLE,LENS,BOULOGNE,ARRAS,HENIN,VALENCIENNES,DOUAI}/Shapefiles/FR*.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D059*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2

# 62 - Pas-de-Calais : DUNKERQUE, CALAIS, BOULOGNE-SUR-MER, LENS, ARRAS, HENIN, VALENCIENNES, DOUAI, LILLE
python rasterize.py --shapefiles Urban_Atlas2012/FR*{DUNKERQUE,CALAIS,LILLE,LENS,BOULOGNE,ARRAS,HENIN,VALENCIENNES,DOUAI}/Shapefiles/FR*.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D062*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2

# 63 - Puy-de-Dôme : CLERMONT-FERRAND
python rasterize.py --shapefiles Urban_Atlas2012/FR*CLERMONT*/Shapefiles/FR*.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D063*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2 

# 72 - Sarthe : LE MANS
python rasterize.py --shapefiles Urban_Atlas2012/FR*MANS/Shapefiles/FR*.shp --dataset 'UA2012' BDORTHO_libre/BDORTHO*D072*/BDORTHO/1_DONNEES_LIVRAISON_*/BDO_*/*.jp2 

