#!/bin/bash

curl 'https://civclassic.miraheze.org/w/index.php?title=MtA_Map&action=edit' 2>>import-mta.stderr \
| tee "MtA_Map_`date -Iseconds`.html" \
| grep -E '^(circle|rect|poly) .*\.png.*' \
| while read line; do
    imgfile="$(echo "$line" | grep -oE 'File:[^|]+\.png' | sed 's/ /+/g')"

    imgurl="$(curl "https://civclassic.miraheze.org/w/api.php?action=query&titles=${imgfile}&prop=imageinfo&iilimit=50&iiprop=url&format=json" 2>>import-mta.stderr | tee -a import-mta.curl \
    | grep -oE '"url":"[^"]+"' | cut -d\" -f4)"

    echo "$line" | sed -E 's#(.*)\[\[(File:[^|]+\.png)(.*)\]\]#\1['"$imgurl"' \3]#g'
done \
| tee "with_images_`date -Iseconds`.txt" \
| sed -E 's#^circle (\S+) (\S+) (\S+) \[ ?(.+\.png) (.*)\]#{"x":\1,"z":\2,"radius":\3,"image":"\4","name":"\5"}#g' \
| sed -E 's#^rect (\S+) (\S+) (\S+) (\S+) \[ ?(.+\.png) (.*)\]#{"polygon":[[\1,\2],[\1,\4],[\3,\4],[\3,\2]],"image":"\5","name":"\6"}#g' \
| sed -E 's#^poly ([-0-9 ]+) \[ ?(.+\.png) (.*)\]#{"polygon":[\1],"image":"\2","name":"\3"}#g' \
