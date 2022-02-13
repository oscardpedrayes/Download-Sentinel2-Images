from osgeo import ogr
SHP_PATH = "/MTN50_ETRS89_Peninsula_Baleares_Canarias.shp"
OUTPUT_FILENAME = "MTN50.txt"

file = ogr.Open(SHP_PATH)
shape = file.GetLayer(0)
#first feature of the shapefile
feature = shape.GetFeature(2)
count = shape.GetFeatureCount()

# empty file 
open(OUTPUT_FILENAME, 'w').close()

for i in range(count):
    feature = shape.GetFeature(i)
    val = feature.ExportToJson()
    number = val.split(':')[6].split(',')[0].replace('"','').replace(" ","")
    coors = val.split(':')[4].replace('[','').replace(']','').replace(',','').replace('}','').split(' ')[1:-1]
    x1 = float(coors[0])
    y1 = float(coors[1])
    x2 = float(coors[0])
    y2 = float(coors[1])
    # Get max and min values
    for i in range(int(len(coors)/2)):
        i=i*2
        xtemp= float(coors[i])
        ytemp= float(coors[i+1])
        if x1>xtemp:
            x1=xtemp
        if y1<ytemp:
            y1=ytemp
        if x2<xtemp:
            x2=xtemp
        if y2>ytemp:
            y2=ytemp

    line = str(number) + " " + str(x1) + " " + str(y1) + " " + str(x2) + " " + str(y2)
    # Save locations on file
    with open(OUTPUT_FILENAME, 'a') as f:
        print(line, file=f)

