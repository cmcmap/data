import sys
import os
import json
import math
import re
import urllib.request
from helpers import ACRONYMS, FLAG_REDIRECTS

from mwclient import Site
from mwclient.errors import LoginError
import wikitextparser as wtp

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
    MODE = os.environ.get('MODE', 'OFFLINE')
    SANDBOX = False
    USER = os.environ.get('USERNAME', '')
    PASSWORD = os.environ.get('PASSWORD', '')
    # ------------------------------------------------

    if MODE == "SANDBOX":
        SANDBOX = True
        MODE == "WIKI"
    # ["MARKDOWN","WIKI","OFFLINE","SANDBOX","USERNAME","PASSWORD"]
   
    # Get the latest claims json
    with open('land_claims.civmap.json', 'r') as file:
      data = json.loads(file.read())

    # Calculate and sort the area of every polygon, combining ones from the same nation
    owner = {}
    areas_t = {}
    areas = {}
    shortnames = {}

    for feat in data["features"]: 
        name = feat["name"]
        territory = feat["name"]
        if MERGE:
            nation = ( re.sub("\(|\)","",re.search("(^[^()]+$)|\((.*)\)",name.replace("\n"," ")).group()))
            territory = name.replace("\n"," ").strip()
            if "shortname" in feat:
                shortnames[nation] = feat["shortname"]
                
            if ACRONYMS.get(nation) is not None:
                nation = ACRONYMS.get(nation)
            if ACRONYMS.get(territory) is not None:
                territory = ACRONYMS.get(territory)
        else:
            nation = name
        
        if territory[0] == "(": # Handle specific edge cases
            territory = nation
        owner[territory] = nation

        area = 0
        if "polygon" in feat:
             for poly in feat["polygon"]:
                area += polygon_area(poly)

        # Nation
        for nat in nation.split('/'):
            if nat in areas:
                areas[nat] += area
            else:
                areas[nat] = area
        # Territories
        if territory in areas_t:
            areas_t[territory] += area
        else:
            areas_t[territory] = area

    areas_sorted = {}    
    areas_sorted_keys = sorted(areas,key=areas.get,reverse=True)
    for w in areas_sorted_keys:
        areas_sorted[w] = areas[w]

    areas_t_sorted = {}    
    areas_t_sorted_keys = sorted(areas_t,key=areas_t.get,reverse=True)
    for w in areas_t_sorted_keys:
        areas_t_sorted[w] = areas_t[w]

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
                # print(key,are)
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

        # ------------------------------------------
        # Generate the nation table
        #
        
        nation_table = ""
        
        nation_table += "{| class=\"wikitable sortable\"\n|+\n!Rank\n!Nation\n!Area in km²\n!% of Map Area\n|-\n"
        nation_table += ("|-\n|{}\n|{}\n|{}\n|{}\n".format(0,"''[[CivClassic]]''",round(WORLD_AREA/1000000,3),100))
        i = 1
        for key in areas_sorted.keys():
            are = round(areas[key]/1000000,3)
            per = round ((areas[key]/WORLD_AREA)*100,3)
            #print(key,are)
            nation_txt = "[[{}]]".format(key)
            if key in flag_template_whitelist or key in FLAG_REDIRECTS:
                nation_txt = "{{{{flag|{}}}}}".format(key)
            elif key in shortnames:
                if shortnames[key] in flag_template_whitelist:
                    nation_txt = "{{{{flag|{}}}}}".format(shortnames[key])
            nation_table += "|-\n|{}\n|{}\n|{}\n|{}\n".format(i,nation_txt,are,per)
            i = i+1
        nation_table += "|}\n"

        # ------------------------------------------------
        # Generate the territory table
        #
        territory_table = ""
        territory_table += "{| class=\"wikitable sortable\"\n|+\n!Rank\n!Territory\n!Area in km²\n!% of Map Area\n|-\n"
        territory_table += ("|-\n|{}\n|{}\n|{}\n|{}\n".format(0,"''[[CivClassic]]''",round(WORLD_AREA/1000000,3),100))
        i = 1
        for key in areas_t_sorted.keys():
            are = round(areas_t[key]/1000000,3)
            per = round ((areas_t[key]/WORLD_AREA)*100,3)

            territory = re.sub("\(.*?\)","",key).strip()
            nation  = owner[key]
            #print(territory,nation)
            territory_txt = key

            if territory == nation:
                territory_txt = "[[{}]]".format(key)
                if key in flag_template_whitelist or key in FLAG_REDIRECTS:
                    territory_txt = "{{{{flag|{}}}}}".format(key)
                elif key in shortnames:
                    if shortnames[key] in flag_template_whitelist:
                        territory_txt = "{{{{flag|{}}}}}".format(shortnames[key])
            else: # This is a territory
                flag = ""
                # Check if terrritory has flag of its own
                if territory in flag_template_whitelist or territory in FLAG_REDIRECTS:
                    flag = "{{{{flagicon|{}}}}} ".format(territory)
                # -- disabled code that would've placed the parent nation's flag if the territory lacked its own
                #else:
                #    if nation in flag_template_whitelist or nation in FLAG_REDIRECTS:
                #        flag = "{{{{flagicon|{}}}}} ".format(nation)
                #    elif nation in shortnames:
                #        if shortnames[nation] in flag_template_whitelist:
                #            flag = "{{{{flagicon|{}}}}} ".format(shortnames[nation])

                territory_txt = flag + "[[{}|{}]]".format(territory,key)

            territory_table += "|-\n|{}\n|{}\n|{}\n|{}\n".format(i,territory_txt,are,per)
            i = i+1
        territory_table += "|}\n"

        #print(territory_table)

        # ---------------------------------------------------
        # Upload the table to civwiki
        #
        if SANDBOX == False:
            page = site.pages['List_of_nations_by_area']
        else:
            page = site.pages['List_of_nations_by_area/Sandbox']
        text = page.text()
        parsed = wtp.parse(text)
        # print(parsed.pformat())
        for section in parsed.sections:
            if section.title == "Nations by area":
                section.contents = nation_table
            if section.title == "Territories by area":
                section.contents = territory_table
        if MODE == "OFFLINE":
            with open('areas.txt','w') as f:
                f.write(parsed.string)
        else:
            site.login(USER,PASSWORD)
            if page != parsed.string:
                page.edit(parsed.string,"Automated Table Update")

if __name__ == "__main__":
    main(sys.argv[1:])
