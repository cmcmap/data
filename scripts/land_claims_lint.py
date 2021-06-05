import json

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
    with open('data/land_claims.civmap.json') as f:
        data = json.loads(f.read())
except NameError:
    print ("ERROR: FAILED TO LOAD JSON")
    print (NameError)
    quit()
else:
    print ("Successfully loaded Json")

if "features" in data:
    for feat in data["features"]:
        # ------- NAME
        if not "name" in feat:
            print("ERROR: LACKS name")
            print(feat)
        elif feat["name"] in names:
            print(feat["name"],"- several claims share this name, mistake?")
        else:
            names.append(feat["name"])
        # ------- COLOR
        if not "color" in feat:
            print("ERROR: LACKS color")
            print(feat)
        elif len(feat["color"]) != 7 or feat["color"][0] != "#":
            print(feat["color"])
            print("ERROR: Invalid Color")
            print(feat)
        # ------- POLYGON
        if not "polygon" in feat:
            print("ERROR: LACKS polygon")
            print(feat)
        elif not type(feat["polygon"]) is list:
            print("ERROR: Invalid Claims Polygon")
            print(feat)
        elif depthCount(feat["polygon"]) != 3:
            print("ERROR: Invalid Polygon Depth")
            print(feat)
        # ------- ID
        if not "id" in feat:
            print("ERROR: LACKS id")
            print(feat)
        elif feat["id"] in ids:
            print("ERROR: Duplicated ID",feat["id"])
            print(feat)
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

print("lint complete")
