import os
import geopandas as gpd
import folium
import webbrowser

dirname = os.path.dirname(__file__)
emprise = gpd.read_file(dirname + '/data/emprise.shp')

#Montpellier coordinates, used as a center for Leaflet map
#m = folium.
m = folium.Map(location= [43.610015, 3.876397], zoom_start=12)

NDVI50_2022 = gpd.read_file(dirname + '/data/NDVI50_2022.shp')
NDVI_2022, NDVI_2023 = gpd.read_file(dirname + '/data/tif/NDVI_2022_masked.tif'), gpd.read_file(dirname + '/data/tif/NDVI_2023_masked.tif')

folium.LayerControl().add_to(m)
folium.GeoJson(NDVI_2022, name = "NDVI 2022").add_to(m)
folium.GeoJson(NDVI_2023, name = "NDVI 2023").add_to(m)

m.save("map.html")
webbrowser.open("map.html")
m