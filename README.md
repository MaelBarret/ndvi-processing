This project is , using Python for automation and R to process data.
It still requires to be developed in order to be used as a fully functionnal application.
It's purpose is to be used as a model for other projects.

Automation's steps:

  1- Fetch satellite raster data (Sentinel 2: [click here](https://scihub.copernicus.eu/dhus)) covering a specified mask. The query is looking for the least cloud coverage.
  ![Mask](./illustrations/area_mask.jpg)
  ![Sentinel2](./illustrations/sentinel2_bands.jpg)
  
  2- Clip satellite data with the mask
  ![Clip mask](./illustrations/mask_clip.jpg)
  
  3- Process NDVI
  ![NDVI](./illustrations/NDVI.jpg)
  
  4- Open NDVI raster with R and process data distribution
  ![NDVI distribution](./illustrations/NDVI_distribution.jpg)
  
  5- Write two rasters with NDVI value >25 and >50
  
  6- Display filtered NDVI raster on a Leaflet map, usin Folium plugin
  ![Leaflet](./illustrations/NDVI_leaflet.jpg)
  
Requirements:

  - Change paths according to your local environment
  - Python
  - R
