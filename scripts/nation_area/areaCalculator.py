import sys, getopt
import json
import math
import re
import urllib.request
from helpers import ACRONYMS, FLAG_REDIRECTS

from mwclient import Site
from mwclient.errors import LoginError
import wikitextparser as wtp

from secret import USER,PASSWORD

def polygon_area(vertices):
    psum = 0
    nsum = 0

    for i in range(len(vertices)):
        sindex = (i + 1) % len(vertices)
        prod = vertices[i][0] * vertices[sindex][1]
        psum += prod

    for i in range(len(vertices)):
        sindex = (i + 1) % len(vertices)
        prod = vertices[sindex][0] * vertices[i][1]
        nsum += prod

    return abs(1/2*(psum - nsum))

def main(argv):
    # ------------- Constant Variables ----------------
    MERGE = True
    WORLD_AREA = math.pi * (13000*13000)
    MODE = "OFFLINE"
    DATA_URL = "https://githubraw.com/ccmap/data/master/land_claims.civmap.json"
    SANDBOX = False
    # ------------------------------------------------

    try: 
        opts, args = getopt.getopt(argv,"h",["markdown","wiki","offline","sandbox","help"])
    except getopt.GetoptError:
        print("areaCalculator.py --wiki")
        sys.exit(2)
    for opt,arg in opts:
        if opt in ('-h','--help'):
            print ("--markdown , --wiki , --offline , --sandbox , --help")
        if opt in "--markdown":
            MODE = "MARKDOWN"
        if opt in "--wiki":
            MODE = "WIKI"
        if opt in "--offline":
            MODE = "OFFLINE"
        if opt in "--sandbox":
            MODE = "WIKI"
            SANDBOX = True
    # Get the latest claims json
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url=DATA_URL, headers=headers)

    with urllib.request.urlopen(req) as url:
      data = json.loads(url.read().decode())

    # Calculate and sort the area of every polygon, combining ones from the same nation
    areas = {}
    shortnames = {}

    for feat in data["features"]: 
        name = feat["name"]
        if MERGE:
            nation = ( re.sub("\(|\)","",re.search("(^[^()]+$)|\((.*)\)",name.replace("\n"," ")).group()))
            if "shortname" in feat:
                shortnames[nation] = feat["shortname"]
                
            if ACRONYMS.get(nation) is not None:
                nation = ACRONYMS.get(nation)
        else:
            nation = name

        area = 0
        if "polygon" in feat:
             for poly in feat["polygon"]:
                area += polygon_area(poly)
        else:
            print(feat)

        if nation in areas:
            areas[nation] += area
        else:
            areas[nation] = area

    areas_sorted = {}    
    areas_sorted_keys = sorted(areas,key=areas.get,reverse=True)
    for w in areas_sorted_keys:
        areas_sorted[w] = areas[w]

    # Render the table

    if MODE == "MARKDOWN":
        with open('areas.md','w') as f:
            f.write("#|Nation|Area (km²)|% of Map Area\n")
            f.write(":---:|:---:|:---:|:---:|\n")
            f.write("{}|{}|{}|{}\n".format(0,"*CivClassic*",round(WORLD_AREA/1000000,3),100))

            i = 1
            for key in areas_sorted.keys():
                are = round(areas[key]/1000000,3)
                per = round ((areas[key]/WORLD_AREA)*100,3)
                print(key,are)
                f.write("{}|{}|{}|{}\n".format(i,key,are,per))
                i = i + 1
    if MODE == "WIKI" or MODE == "OFFLINE":
        # Get all countries with a flag template
        flag_template_whitelist = []

        ua = "AreaListCalculator/0.0.1 Smal"
        site = Site('civwiki.org',clients_useragent=ua)

        category = site.categories['All country data templates']
        for page in category:
            flag_template_whitelist.append(page.name[len("Template:Country data")+1:])

        # Generate the wiki table
        new_table = ""
        new_table += "{| class=\"wikitable sortable\"\n|+\n!Rank\n!Nation\n!Area in km²\n!% of Map Area\n|-\n"
        new_table += ("|-\n|{}\n|{}\n|{}\n|{}\n".format(0,"''[[CivClassic]]''",round(WORLD_AREA/1000000,3),100))
        i = 1
        for key in areas_sorted.keys():
            are = round(areas[key]/1000000,3)
            per = round ((areas[key]/WORLD_AREA)*100,3)
            #print(key,are)
            nation_txt = "[[{}]]".format(key)
            if key in flag_template_whitelist:
                nation_txt = "{{{{flag|{}}}}}".format(key)
            elif key in shortnames:
                if shortnames[key] in flag_template_whitelist:
                    nation_txt = "{{{{flag|{}}}}}".format(shortnames[key])
            new_table += "|-\n|{}\n|{}\n|{}\n|{}\n".format(i,nation_txt,are,per)
            i = i+1
        new_table += "|}"

        # Upload the table to civwiki
        if SANDBOX == False:
            page = site.pages['List_of_nations_by_area']
        else:
            page = site.pages['List_of_nations_by_area/Sandbox']
        text = page.text()
        parsed = wtp.parse(text)
        
        for section in parsed.sections:
            if section.title == "Nations by area":
                section.contents = new_table
        print(parsed.string)
        if MODE == "OFFLINE":
            with open('areas.txt','w') as f:
                f.write(parsed.string)
        else:
            site.login(USER,PASSWORD)
            page.edit(parsed.string,"Automated Table Update")
        

if __name__ == "__main__":
    main(sys.argv[1:])
