import json
import sys

#-----------
#   Checks for common errors in ccmap polygon data and prints them all to console
#   Exists with code 1 when any error was found
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
    with open('land_claims.civmap.json') as f:
        data = json.loads(f.read())
except NameError:
    print("ERROR: FAILED TO LOAD JSON")
    print(NameError)
    sys.exit(1)

if "features" not in data:    
    print("ERROR: Features Field not found")
    sys.exit(1)

# whether any of the features has an error (results in exit code 1 after all checks finish)
any_feat_error = False

for feat in data["features"]:
    # whether this feature has an error (prints the feature after all checks finish)
    feat_error = False
    # ------- NAME
    if not feat.get("name", ""):
        print("ERROR: LACKS name")
        feat_error = True
    elif feat["name"] in names:
        print("WARNING:", feat["name"], "- several claims share this name, mistake?")
    else:
        names.append(feat["name"])
    # ------- COLOR
    if not "color" in feat:
        print("ERROR: LACKS color")
        feat_error = True
    elif len(feat["color"]) != 7 or feat["color"][0] != "#":
        print("ERROR: Invalid Color:", feat["color"])
        feat_error = True
    # ------- POLYGON
    if not "polygon" in feat:
        print("ERROR: LACKS polygon")
        feat_error = True
    elif not type(feat["polygon"]) is list:
        print("ERROR: Invalid Claims Polygon")
        feat_error = True
    elif depthCount(feat["polygon"]) != 3:
        print("ERROR: Invalid Polygon Depth", depthCount(feat["polygon"]))
        feat_error = True
    # ------- ID
    if not feat.get("id", ""):
        print("ERROR: LACKS id")
        feat_error = True
    elif feat["id"] in ids:
        print("ERROR: Duplicated ID", feat["id"])
        feat_error = True
    else:
        ids.append(feat["id"])

    # ------- WARNINGS 
    if DISPLAY_WARNINGS:
        if "collection_id" in feat:
            print("WARNING: HAS UNECESSARY collection_id",feat["name"])
        #if not "shortname" in feat:
        #    print("WARNING: LACKS shortname", feat["name"])
        if not "declutter" in feat:
            print("WARNING: LACKS declutter", feat["name"])

    if feat_error:
        any_feat_error = True
        print(feat)

print("lint complete")

if any_feat_error:
    sys.exit(1)
else:
    sys.exit(0)
