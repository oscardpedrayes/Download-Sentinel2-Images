import csv
import numpy as np
import sys
import gdal
from osgeo import ogr, osr
import math
import os
from matplotlib.path import Path
from subprocess import Popen, PIPE
import shutil

maxInt = sys.maxsize # Increase max size of csv fields
while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

# PNOA to read
PNOA = "0162"

# Obtain the data
CSV = "sigpac/PNOA_" + PNOA + ".csv"
TILES = "SENTINEL_Datasets/" + PNOA + "/Images"
TILES_CSV = "/data.csv"
TILES_PART = ["_1/","_2/"]

# Save folders
CROPS = "SENTINEL_Datasets/"+PNOA+"/Images/"
MASK = "SENTINEL_Datasets/"+PNOA+"/Labels/"

# Check dirs
if not (os.path.isfile(CSV) and  os.path.exists(TILES+TILES_PART[0]) and os.path.exists(TILES+TILES_PART[1]) ) :
    print("Error: Wrong files/directories")
    exit()

# Create dirs
if not os.path.exists(CROPS):
    os.mkdir(CROPS)
if not os.path.exists(MASK):
    os.mkdir(MASK)

# Initialize variables
t = None

### Associate a color to a terrain usage
def getColor(usage):
    if usage == "IM": return [255, 0, 0]
    if usage == "PS": return [255, 127, 0]
    if usage == "PR": return [255, 255, 0]
    if usage == "FO": return [127, 255, 0]
    if usage == "ED" or usage=="ZU": return [0, 255, 0]
    if usage == "TA": return [0, 255, 127]
    if usage == "PA": return [255, 0, 255]
    if usage == "CA": return [0, 255, 255]
    if usage == "AG": return [0, 127, 255]
    if usage == "FS" or usage =="FY": return [0, 0, 255]
    if usage == "VI": return [127, 0 , 255]
    else: return [0, 0, 0]



with open(CSV, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Clean coordinates string into array
        coors = row['dn_geom'].replace('POLYGON ((', '').replace(')','').replace('(','').replace(',',' ').split(' ')
        # Get id
        parcelId =row['dn_oid']
        # Get usage an dassociate a color to it
        usage = row['uso_sigpac']
        color = getColor(usage)

        # Allocate memory for geometry
        parcel_lines = ogr.Geometry(ogr.wkbLinearRing)
        for i in range(int(len(coors)/2)):
            i=i*2
            xtemp= float(coors[i])
            ytemp= float(coors[i+1])
            # Add points to geometry
            parcel_lines.AddPoint_2D(xtemp,ytemp)

        # Close geometry
        parcel_lines.AddPoint_2D(float(coors[0]), float(coors[1]))

        # Create polygon
        parcelGeom = ogr.Geometry(ogr.wkbPolygon)
        parcelGeom.AddGeometry(parcel_lines)

        # Iterate through tiles
        for part in TILES_PART:
            with open(TILES + part + TILES_CSV, "r") as listiles:
                for tile in listiles:
                    tile = tile.split(';')
                    filename = tile[0]
                    if ".tif" in filename:
                        # Read coordinates
                        x1 = float(tile[1]) 
                        x2 = float(tile[2])  
                        y2 = float(tile[3])  
                        y1 = float(tile[4])  

                        # Read file to obtain metadata
                        if (t == None):
                            ds = gdal.Open(TILES + part + filename) 
                            width = ds.RasterXSize
                            height = ds.RasterYSize

                            # Get CRS from dataset 
                            crs = osr.SpatialReference()
                            crs.ImportFromWkt(ds.GetProjectionRef())

                            # create lat/long crs with ETR89 datum

                            crsGeo = osr.SpatialReference()
                            crsGeo.ImportFromEPSG(4258) # 4326 is the EPSG id of lat/long crs 4258
                            t = osr.CoordinateTransformation(crs, crsGeo)

                        # Transform coordinates to ETRS89 lat/long
                        x1, y1, z1 = t.TransformPoint(x1, y1)
                        x2, y2, z2 = t.TransformPoint(x2, y2)

                        # Add more area to prevent borders without mask
                        x1= x1 - 0.0001
                        x2= x2 + 0.0001
                        y1= y1 + 0.0001
                        y2= y2 - 0.0001

                        # Add points to the geometry
                        tileLines = ogr.Geometry(ogr.wkbLinearRing)
                        tileLines.AddPoint_2D(x1, y1)
                        tileLines.AddPoint_2D(x1, y2)
                        tileLines.AddPoint_2D(x2, y2)
                        tileLines.AddPoint_2D(x2, y1)
                        # Close geometry
                        tileLines.AddPoint_2D(x1, y1)

                        # Create polygon
                        tileGeom = ogr.Geometry(ogr.wkbPolygon)
                        tileGeom.AddGeometry(tileLines)
                        #print()
                        #print(parcelGeom)
                        #print(tileGeom)
                        #print()

                        vertices = [[0.0,0.0]] # Placeholder values
                        
                        # If there is an intersection continue to process it
                        if (parcelGeom.Intersects(tileGeom)):
                            try:
                                print(parcelId)
                                # Get the intersection geometry
                                parcelIntersec = parcelGeom.Intersection(tileGeom)
                                # Obtain the coordinates from the geometry   
                                parcelIntersec_coors = str(parcelIntersec).replace("MULTI","").replace('POLYGON ((', '').replace(')','').replace('(','').replace(',',' ').split(' ')

                                # Allocate memory for coordinates
                                parcelInstersec_coors_tile = np.zeros((int(len(parcelIntersec_coors))))
                                # Iterate throught coordinates and convert them to pixel locations
                                for j in range(int(len(parcelIntersec_coors)/2)):
                                    j=j*2
                                    xtemp_= float(parcelIntersec_coors[j])
                                    ytemp_= float(parcelIntersec_coors[j+1])
                                    # Call GDALINFO to get Pixels location
                                    cmd = ['gdallocationinfo', '-l_srs', 'EPSG:4258', TILES + part + filename, str(xtemp_), str(ytemp_)]
                                    p = Popen(cmd, stdout=PIPE)
                                    p.wait()
                                    val = p.stdout.read()
                                    # Format string to get the values
                                    val= str(val).split('(')[1].split(')')[0].replace('P','').replace('L','').split(',')
                                    # Add pixels location as vertices
                                    vertices = np.append(vertices, [[val[1], val[0]]], axis = 0)
                                                
                                # Remove the placeholder
                                vertices = vertices[1:]

                                # Allocate memory for the mask image
                                img = np.zeros((height, width, 3), dtype=int)
                                try:
                                    # Create Path from vertices
                                    path = Path(vertices)
                                    # Create a mesh grid for the whole image
                                    ym, xm = np.mgrid[:height, :width]
                                    # mesh grid to a list of points
                                    points = np.vstack((ym.ravel(), xm.ravel())).T
                                    grid = path.contains_points(points, None, -0.5)
                                    # Mask with points inside a polygon
                                    mask = grid.reshape(height, width)

                                    # Check if mask already exist
                                    if os.path.isfile(MASK + filename):
                                        #    Load the mask image
                                        ds = gdal.Open(MASK + filename)
                                        nbands = ds.RasterCount
                                        img = np.random.randn(ds.RasterYSize, ds.RasterXSize, nbands)
                                        for n in range(nbands):
                                            img[:, :, n] = ds.GetRasterBand(n+1).ReadAsArray() 
                                        ds = None # flush data                                  
                                    else: # First time seeing that crop, therefore save it 
                                        shutil.copyfile(TILES + part + filename, CROPS + filename)                            

                                    # Draw mask onto de image
                                    for y_ in range(height):
                                        for x_ in range(width):
                                            if (mask[y_, x_]):                                                             
                                                img[y_, x_, 0] =  int(color[0])
                                                img[y_, x_, 1] =  int(color[1])
                                                img[y_, x_, 2] =  int(color[2])

                                    # Save mask onto disk
                                    driver = gdal.GetDriverByName("GTiff")
                                    outdata = driver.Create(MASK + filename, width, height, 3, gdal.GDT_Byte)
                                    for band in range(3):
                                        outdata.GetRasterBand(band+1).WriteArray(img[:, :, band])                                  
                                    outdata.FlushCache() 
                                    outdata = None

                                except Exception as e1:
                                    print("AN EXCEPTION HAS OCCURRED (Creating mask)")
                                    print(e1)
                            except Exception as e2:
                                print("AN EXCEPTION HAS OCCURRED (Intersection)")
                                print(e2)
