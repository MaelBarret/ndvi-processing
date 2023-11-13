# load spatial packages
library(raster)
library(rgdal)
library(rgeos)
library(RColorBrewer)

# turn off factors
options(stringsAsFactors = FALSE)

naip_multispectral_st4 <- stack("C:/Users/maelb/Desktop/Satellite/data/b4_2022_masked.tif")
naip_multispectral_st8 <- stack("C:/Users/maelb/Desktop/Satellite/data/b8_2022_masked.tif")

# convert data into rasterbrick for faster processing
naip_multispectral_br4 <- brick(naip_multispectral_st4)
naip_multispectral_br8 <- brick(naip_multispectral_st8)

# calculate ndvi with naip
naip_multispectral_br8
## class      : RasterLayer 
## dimensions : 2312, 4377, 10119624  (nrow, ncol, ncell)
## resolution : 1, 1  (x, y)
## extent     : 457163, 461540, 4424640, 4426952  (xmin, xmax, ymin, ymax)
## crs        : +proj=utm +zone=13 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs 
## source     : memory
## names      : m_3910505_nw_13_1_20130926_crop.4 
## values     : 0, 255  (min, max)

# calculate NDVI using the red (band 1) and nir (band 4) bands
naip_ndvi <- (naip_multispectral_br8 - naip_multispectral_br4) / (naip_multispectral_br8 + naip_multispectral_br4)

# plot the data
plot(naip_ndvi,
     main = "NDVI of Cold Springs Fire Site - Nederland, CO \n Pre-Fire",
     axes = FALSE, box = FALSE)

hist(naip_ndvi,
main = "Distribution du NDVI en juin 2022\n sur la ville de Montpellier",
col = "springgreen",
xlab = "NDVI",
ylab = "Nombre de pixels")

# Check if the directory exists using the function you created last week
#check_create_dir("data/week-07/outputs/")

# Export your raster
writeRaster(x = naip_ndvi,
              filename="C:/Users/maelb/Desktop/Satellite/data/tif/naip_ndvi_2022_prefire.tif",
              format = "GTiff", # save as a tif
              datatype='INT2S', # save as a INTEGER rather than a float
              overwrite = TRUE)  # OPTIONAL - be careful. This will OVERWRITE previous files.