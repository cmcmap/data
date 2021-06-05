import json
import sys

#-----------
#   Attempts to check for common errors in ccmap polygon data and prints them to console
#       - warning: crude and untested
#------------

def depthCount(lst):
    'takes an arbitrarily nested list as a parameter and returns the maximum depth to which the list has nested sub-lists.'
    if isinstance(lst, list):
        return 1 + max(depthCount(x) for x in lst)
    else:
        return 0
data = []
ids = []
names = []

DISPLAY_WARNINGS = True

try:
    with open('../land_claims.civmap.json') as f:
        data = json.loads(f.read())
except NameError:
    print ("ERROR: FAILED TO LOAD JSON")
    print (NameError)
    sys.exit(1)
else:
    print ("Successfully loaded Json")

if "features" in data:
    for feat in data["features"]:
        # ------- NAME
        if not "name" in feat:
            print("ERROR: LACKS name")
            print(feat)
            sys.exit(1)
        elif feat["name"] in names:
            print(feat["name"],"- several claims share this name, mistake?")
        else:
            names.append(feat["name"])
        # ------- COLOR
        if not "color" in feat:
            print("ERROR: LACKS color")
            print(feat)
            sys.exit(1)
        elif len(feat["color"]) != 7 or feat["color"][0] != "#":
            print(feat["color"])
            print("ERROR: Invalid Color")
            print(feat)
            sys.exit(1)
        # ------- POLYGON
        if not "polygon" in feat:
            print("ERROR: LACKS polygon")
            print(feat)
            sys.exit(1)
        elif not type(feat["polygon"]) is list:
            print("ERROR: Invalid Claims Polygon")
            print(feat)
            sys.exit(1)
        elif depthCount(feat["polygon"]) != 3:
            print("ERROR: Invalid Polygon Depth")
            print(feat)
            sys.exit(1)
        # ------- ID
        if not "id" in feat:
            print("ERROR: LACKS id")
            print(feat)
            sys.exit(1)
        elif feat["id"] in ids:
            print("ERROR: Duplicated ID",feat["id"])
            print(feat)
            sys.exit(1)
        else:
            ids.append(feat["id"])
        
        # ------- WARNINGS 
        if DISPLAY_WARNINGS:
            if "collection-id" in feat:
                print("WARNING: HAS UNECESSARY collection-id",feat["name"])
            #if not "shortname" in feat:
            #    print("WARNING: LACKS shortname", feat["name"])
            if not "declutter" in feat:
                print("WARNING: LACKS declutter", feat["name"])
else:
    print("ERROR: Features Field not found")
    sys.exit(1)

print("lint complete")
sys.exit(0)
