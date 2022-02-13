
INSTANCE_ID =  ""

LAYER_NAME = 'BANDS-S2-L2A'  # e.g. TRUE-COLOR-S2-L1C
URL = ''
PNOA_IMAGES =["0158"] 
MTN50_FILE = ""


import datetime
import numpy as np
import csv
import os
import gdal
import math
from sentinelhub import SHConfig, WcsRequest, BBox, CRS, MimeType, CustomUrlParam, get_area_dates, DataSource
from osgeo import ogr, osr

import sys
maxInt = sys.maxsize # Increase max size of csv fields

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

# Load account config
if INSTANCE_ID:
    config = SHConfig()
    config.instance_id = INSTANCE_ID
else:
    config = None


for pnoaImage in PNOA_IMAGES:
    with open(MTN50_FILE, "r") as f:
        for line in f:
                mtn50 = line.split(' ')[0]
                if mtn50 == pnoaImage:
                    # Read coordinates from file
                    x1 = float(line.split(' ')[1])
                    y1 = float(line.split(' ')[2])
                    x2 = float(line.split(' ')[3])
                    y2 = float(line.split(' ')[4])
  
                    # Longitude divides by 2, to make the image smaller
                    x1_5 = x1 + (abs(x2-x1)/2.0) 
                    X1 = [x1, x1_5]
                    X2= [x1_5, x2]

                    # Make a request for each subimage
                    for x in range(2):

                        folder = mtn50 + '_' + str(x+1)
                        print(folder, X1[x],y1,X2[x],y2)

                        # Location of the parcel
                        coords_wgs84 = [X1[x], y2, X2[x], y1]

                        bbox = BBox(bbox=coords_wgs84, crs=CRS.WGS84)

                        # Create dir
                        if not os.path.exists(URL + folder):
                            os.mkdir(URL + folder)

                        # Config request
                        request = WcsRequest(
                            data_source=DataSource.SENTINEL2_L2A,
                            data_folder=URL + folder,
                            layer=LAYER_NAME,
                            bbox=bbox,
                            time=('2020-07-03'), #time=('2020-07-20'), #17, 08
                            #time=('2018-04-30','2018-08-15'),
                            #time='latest',
                            time_difference=datetime.timedelta(hours=4),
                            resx='10m',
                            resy='10m',
                            image_format=MimeType.TIFF_d32f,
                            config=config
                        )

                        # Send request and retrieve the data
                        wms_bands_img = request.get_data(save_data=True)
                        print(len(wms_bands_img))
                        if len(wms_bands_img)>0:
                            print(wms_bands_img[-1].shape)               

                            # Save coordinates and date in txt file.
                            text_file = open(URL + folder + "/topLeftPoint.txt", "w")
                            n = text_file.write(str(X1[x])+' '+str(y1) + ' ' + str(X2[x]) + ' ' + str(y2) + "\n" + str(request.get_dates()[-1]))
                            text_file.close()
                        exit()





       
