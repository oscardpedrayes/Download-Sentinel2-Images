import csv
import numpy as np
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

CSV = "0346_20200901.csv"
OUTPUT_FILENAME = "CoorList_0346_20200901.txt"

#X_MAX_LENGTH = 0.052
#Y_MAX_LENGTH = 0.03775

# empty file 
open(OUTPUT_FILENAME, 'w').close()

with open(CSV, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Clean coordinates string into array
        coors = row['dn_geom'].replace('POLYGON ((', '').replace(')','').replace('(','').replace(',',' ').split(' ')
        # Assign default values
        x1= float(coors[0])
        y1= float(coors[1])
        x2= float(coors[0])
        y2= float(coors[1])
        # Save image in folder with id as a name
        folder=row['dn_oid']

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

        ## Get actual length
        #xLength = abs(x2-x1)
        #yLength = abs(y1-y2)

        ## Add required length to keep all images the same size
        #if (xLength < X_MAX_LENGTH):
        #    xHalfLeftLength = (X_MAX_LENGTH-xLength)/2.0
        #    x1 = x1 - xHalfLeftLength
        #    x2 = x2 + xHalfLeftLength

        #if (yLength < Y_MAX_LENGTH):
        #    yHalfLeftLength = (Y_MAX_LENGTH-yLength)/2.0
        #    y1 = y1 + yHalfLeftLength
        #    y2 = y2 - yHalfLeftLength

        # Save locations on file
        with open(OUTPUT_FILENAME, 'a') as f:
            print(folder, x1,y1,x2,y2, file=f)