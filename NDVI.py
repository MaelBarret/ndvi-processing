from sentinelsat import SentinelAPI
import os
from dotenv import load_dotenv
import geopandas as gpd
import folium
import webbrowser

load_dotenv()

user = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
dirname = os.path.dirname(__file__)
emprise = gpd.read_file(dirname + '/data/emprise.shp')

#Query fetching raster having least cloud coverage
from shapely.geometry import MultiPolygon, Polygon
def footprint():
    footprint = None
    for i in emprise['geometry']:
        footprint = i
    return footprint

#Get the references of wanted area 
def fetch(period):
    products = api.query(footprint(),
                        period,
                        platformname = 'Sentinel-2',
                        processinglevel = 'Level-2A',
                        cloudcoverpercentage = (0,10)
                        )
    return products

from os.path import exists

def download(period):
    #Download raster of concerned area with the least clouds
    products_gdf = api.to_geodataframe(fetch(period))
    if not len(products_gdf) == 0:
        products_gdf_sorted = products_gdf.sort_values(['cloudcoverpercentage', 'ondemand'], ascending=[True, False])
        products_gdf_sorted.explore()
        if not exists(dirname + '/data/' + products_gdf_sorted['title'][0]):
            is_online = api.is_online(products_gdf_sorted['uuid'][0])
            if is_online:
                api.download(products_gdf_sorted['uuid'][0], dirname + '\data')
            else:
                print(f"Le produit {period} n'est pas disponible en ligne")
                api.trigger_offline_retrieval(products_gdf_sorted['uuid'][0])
        return products_gdf_sorted[:1]
    else:
        print("Il n'y a pas de données pour la période suivante : " + str(period))
        exit()

#Unzipping downloaded files
#import zipfile
#with zipfile.ZipFile(dirname + '/data/', 'r') as zip_ref:
#    info = zip_ref.ZipInfo()
#    info.external_attr = 0o777 << 16
#    zip_ref.write(info)
#    zip_ref.close()
#    zip_ref.extractall(dirname + '/data/')

from pathlib import Path
import rasterio as rio
class NDVI:
    def __init__(self, product):
        # Open Bands 4, 3 and 2 with Rasterio
        self.R10 = product['title'][0]# + '/GRANULE/'#*/IMG_DATA/R10m'
        self.path = dirname + '/data/' + self.R10 + '/' + self.R10 + '.SAFE' + '/GRANULE/'
        self.path = self.path + os.listdir(self.path)[0] + '/IMG_DATA/R10m'

    def getFile(self, path, tail):
        file = []   
        file.extend(Path(path).glob(tail))
        return file

    def bands(self):
        #Extract required bands
        self.b4 = rio.open(self.getFile(self.path, '*_B04_10m.jp2')[0])
        self.b3 = rio.open(self.getFile(self.path, '*_B03_10m.jp2')[0])
        self.b2 = rio.open(self.getFile(self.path, '*_B02_10m.jp2')[0])
        self.b8 = rio.open(self.getFile(self.path, '*_B08_10m.jp2')[0])
        return self.b2, self.b3, self.b4, self.b8
    
    def RGB(self):
        # Create an RGB image
        with rio.open(dirname + '/data/tif/' + self.R10[45:53] + '_RGB.tiff','w',driver='Gtiff', width=self.bands()[2].width, height=self.bands()[2].height,
                    count=3,crs=self.bands()[2].crs,transform=self.bands()[2].transform, dtype=self.bands()[2].dtypes[0]) as rgb:
            rgb.write(self.bands()[0].read(1),1)
            rgb.write(self.bands()[1].read(1),2)
            rgb.write(self.bands()[2].read(1),3)
            rgb.close()

        from rasterio.mask import mask
        emprise_proj = emprise.to_crs({'init': 'epsg:32631'})
        with rio.open(dirname + '/data/tif/' + self.R10[45:53] + '_RGB.tiff') as src:
            out_image, out_transform = mask(src, emprise_proj.geometry, crop=True)
            out_meta = src.meta.copy()
            out_meta.update({"driver": "GTiff",
                            "height": out_image.shape[1],
                            "width": out_image.shape[2],
                            "transform": out_transform})

        with rio.open(dirname + '/data/tif/' + self.R10[45:53] + '_RGB_masked.tif', "w", **out_meta) as dest:
            dest.write(out_image)

    def computeNDVI(self):
        #Read Red(b4) and NIR(b8) as arrays
        red = self.bands()[2].read()
        nir = self.bands()[3].read()

        #Compute ndvi
        self.ndvi = (nir.astype(float)-red.astype(float))/(nir+red)

        # Write NDVI tiff
        self.meta = self.bands()[2].meta
        self.meta.update(driver='GTiff')
        self.meta.update(dtype=rio.float32)

        with rio.open(dirname + '/data/tif/' + self.R10[45:53] + '_NDVI.tif', 'w', **self.meta) as dst:
            dst.write(self.ndvi.astype(rio.float32))

#juin_2022, juin_2023 = ('20220601', '20220630'), ('20230601', '20230630')
#product_juin_2022 , product_juin_2023 = download(juin_2022), download(juin_2023)

#NDVI_juin_2022 = NDVI(product_juin_2022)
#NDVI_juin_2022.RGB()
#NDVI_juin_2022.computeNDVI()
#NDVI_juin_2023 = NDVI(product_juin_2023)
#NDVI_juin_2023.RGB()
#NDVI_juin_2023.computeNDVI()

#Montpellier coordinates, used to center Leaflet map
coords = [43.610015, 3.876397]
zoom_start = 12

#Leaflet mapping using Folium plugin
class Map:
    def __init__(self, center, zoom_start):
        self.center = center
        self.zoom_start = zoom_start
        self.m = folium.Map(location = self.center, zoom_start = self.zoom_start)
    
    def addToMap(self, geojson):
        folium.GeoJson(geojson).add_to(self.m)
    
    def showMap(self):  
        self.m.save("map.html")
        webbrowser.open("map.html")
        return self.m

#Map initialization
map = Map(coords, zoom_start)
#map.addToMap(emprise)

NDVI50_2022 = gpd.read_file(dirname + '/data/NDVI50_2022.shp')
map.addToMap(NDVI50_2022, "NDVI 2022 > 0.5")
folium.LayerControl().add_to(map.m)
map.showMap()

import subprocess
proc = subprocess.run(["C:/Program Files/R/R-4.3.1/bin/RScript",dirname + "/Script.R", ])
#stdout, stderr = proc.communicate()