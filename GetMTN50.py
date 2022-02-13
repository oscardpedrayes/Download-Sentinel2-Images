# This script returns a file with the MTN50 pages found in the CoorList.txt
# created from the Get CoorList.py (using the SIGPAC CSV)
# and another with the parcels it could not find

pathList = "CoorList_0346_20200901.txt"
pathMTN50 = "MTN50.txt"
OUTPUT_FILENAME = "MTN50_0346_20200901.txt"
OUTPUT_FILENAME_NOTFOUND = "NOTFOUND_0346_20200901.txt"

# List to store all MTN50 identifiers
numbersMNT50 = {}
# List to store all not found parcels (if it intersects between two quadrants)
notfound = []

# empty files 
open(OUTPUT_FILENAME, 'w').close()
open(OUTPUT_FILENAME_NOTFOUND, 'w').close()

with open(pathList, "r") as listCoors:
  for line in listCoors:
    line = line.split(' ')
    parcelId = line[0]
    X1 = float(line[1])
    Y1 = float(line[2])
    X2 = float(line[3])
    Y2 = float(line[4])
    found = False

    # Iterate through MTN50 quadrants
    with open(pathMTN50, "r") as listMTN50:
        for lineMTN50 in listMTN50:
            lineMTN50 = lineMTN50.split(' ')
            numberMTN50 = lineMTN50[0]
            x1 = float(lineMTN50[1])
            y1 = float(lineMTN50[2])
            x2 = float(lineMTN50[3])
            y2 = float(lineMTN50[4])
            # Check if it is contained in any quadrant
            if (x1<=X1 and y1>=Y1 and x2>=X2 and y2<=Y2):
                if not numberMTN50 in numbersMNT50:
                    numbersMNT50[numberMTN50] = 1 # Add to the list                   
                else:
                    numbersMNT50[numberMTN50] = numbersMNT50[numberMTN50] + 1
                found = True
                #break # Exit the loop if found           
        # Add parcel to not found if it wasn't
        if (not found):
            notfound.append(parcelId)

#numbersMNT50.sort()


print("Not found: "+ str(len(notfound)))

# Save locations on file
with open(OUTPUT_FILENAME, 'a') as f:
    for n in numbersMNT50:
        print (str(n) + " : "+ str(numbersMNT50[n]), file=f)

with open(OUTPUT_FILENAME_NOTFOUND, 'a') as f:
    print ('\n'.join(notfound), file=f)

print ("Neccesary MTN50 pages were saved in " + OUTPUT_FILENAME)
print ("Not found parcels were saved in " + OUTPUT_FILENAME_NOTFOUND)