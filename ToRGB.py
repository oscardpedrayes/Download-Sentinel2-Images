import numpy as np
import sys
import gdal
from osgeo import ogr, osr
import os

# DATASET to read
DATASET = "20200909"

# Save folders
IMAGES = "SENTINEL_Datasets/"+DATASET+"/Images/"
NEW_IMAGES = "SENTINEL_Datasets/"+DATASET+"/ImagesRGB/"

for root, dirs, files in os.walk(IMAGES, topdown=False):
    for name in files:
        if ".tif" in name:
            # Read
            ds = gdal.Open(root + name)
            nbands = ds.RasterCount
            X = ds.RasterXSize
            Y = ds.RasterYSize
            img = np.random.randn(Y, X, nbands)
            for n in range(nbands):
                img[:,:,n] = ds.GetRasterBand(n+1).ReadAsArray() 
            ds = None # flush data

            newName = name.replace(".tif",".png")
                                        
            # Write
            driver = gdal.GetDriverByName("MEM")
            outdata = driver.Create('' , X, Y, 3, gdal.GDT_Byte)
            for n in range(3):
                outdata.GetRasterBand(n+1).WriteArray(img[:, :, n])
            outdata.FlushCache() 

            driver2 = gdal.GetDriverByName("PNG")
            dst_ds = driver2.CreateCopy(NEW_IMAGES + newName, outdata, strict=0)
            outdata = None
            dst_ds = None
            

              


 