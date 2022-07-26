# usage example:
# curl 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQQOzZDC1xg-TOwS56ld8YOt752JH6T4cnwoF0JvIApYwIoup_VVMtaEK-OQvrae5B_n8UCxmE1DHlS/pub?gid=182771415&single=true&output=tsv' \
# | python3 overlay_from_tsv.py > app/import.civmap.json

# table format: (here, displaying " | " where "\t" would be)
# 0: ... some extra info ...                              <- optional info for readers (e.g. usage, contact)
# 1: Name | x  | z   | Nation | Contact  |                <- primary header
# 2:      |    |     |        | ingame   | Discord        <- secondary header (optional)
# 3: Rome | 70 | -15 | SPQR   | marino94 | @marino#1234   <- data rows
#                                          ^- the empty primary header means: reuse the header left of it, and add the secondary header names to the key names

# output: [{"name":"Rome", "x":70, "z":-15, "nation":"SPQR", "Contact - ingame":"marino94", "Contact - Discord":"@marino#1234"}]

# data rows without an "x" value are ignored
# if a "no_export" column exists, data rows are ignored unless the value is "" or "FALSE"
# if no "name" column exists, the first column without empty cells is used as unique row identifier (sorting)

import json
import re
import sys
import time
from collections import defaultdict

args = sys.argv[1:]

omitted_columns = []
if len(args) >= 1 and args[0].startswith('omit='):
    omitted_columns = args[0].split('=')[1:]
    args = args[1:]

overrides = [arg.split('=', 1) for arg in args]

header_line = next(sys.stdin)  # ignored, contains human info
first_line = next(sys.stdin)
if first_line.endswith('\r\n'):
    nend = -2
elif first_line.endswith('\n'):
    nend = -1
else:
    raise ValueError('unknown line ending in ' + first_line)

header1 = first_line[:nend].split('\t')
header2 = next(sys.stdin)[:nend].split('\t')

headers = []
last_header1 = None
last_header2 = None
for h1, h2 in zip(header1, header2):
    if not h1 and not h2:
        header = ''
    elif not h1:
        headers[-1] = (' - '.join((last_header1, last_header2)))
        h1 = last_header1
        header = ' - '.join((last_header1, h2))
    else:
        header = h1

    if ' ' not in header:
        header = header.lower()

    headers.append(header)

    last_header1 = h1
    last_header2 = h2

print('headers:', headers, file=sys.stderr)


def numify(val):
    """try converting to number"""
    try:
        f = float(val)
        i = int(val)
        if f == i: return i
        return f
    except:
        return val


data = []
for line in sys.stdin:
    cells = line[:nend].split('\t')
    o = { k: numify(v) for k, v in zip(headers, cells) if k and v }
    if 'x' not in o:
        continue
    if 'no_export' in o:
        if o.get('no_export', False) not in ('FALSE', False):
            continue
        del o['no_export']

    for col in omitted_columns:
        if col in o:
            del o[col]

    data.append(o)

# if no "name" column exists, use first column that every entry has set
if 'name' in headers:
    name_col = 'name'
else:
    name_col = next(k for k in headers if all(d[k] for d in data))


def get_name(d):
    # this can only put "unnamed" if there's an explicit "name" col
    return d.get(name_col, '(unnamed)').lower()


data = sorted(data, key=get_name)
print('data:', len(data), 'name_col:', name_col, file=sys.stderr)


def build_props(d):
    props = {
        'name': get_name(d),
    }
    props.update(d)
    replacement = lambda m: str(props.get(m.group(1) if ' ' in m.group(1) else m.group(1).lower(), 'null'))
    for key, override in overrides:
        try:
            props[key] = re.sub(r'\$\{([^}]+)\}', replacement, override)
        except e:
            print('Error overriding', key, e, file=sys.stderr)
    return props


overlay = {
    "name": "Settlements",
    "id": "62da2fc3-60ba-49a4-898b-817051e47d9d",
    "info": {
        "version": "3.0.0-beta3"
    },
    "source": "https://cmcmap.github.io/data/settlements.civmap.json",
    "presentations": [
        {
            "name": "Settlements",
            "style_base": {
                "color": {
                    "default": "#ffcc77",
                    "feature_key": "Zoom Visibility",
                    "categories": {}
                },
                "icon_size": {
                    "default": 8,
                    "feature_key": "Zoom Visibility",
                    "categories": {
                        "1": 18,
                        "2": 16,
                        "3": 14,
                        "4": 12,
                        "5": 10
                    }
                },
                "icon": "circle",
                "label": "$name",
                "opacity": 0,
                "stroke_color": "#000000",
                "stroke_width": {
                    "default": 2,
                    "feature_key": "Zoom Visibility",
                    "categories": {
                    }
                }
            },
            "style_highlight": {
                "opacity": 1,
                "stroke_color": "#ff0000",
                "stroke_width": 2
            },
            "zoom_styles": {
                "-6": {
                    "label": "$nickname",
                    "opacity": {
                        "default": 0,
                        "feature_key": "Zoom Visibility",
                        "categories": {
                            "1": 1
                        }
                    }
                },
                "-4": {
                    "label": {
                        "default": "",
                        "feature_key": "Zoom Visibility",
                        "categories": {
                            "1": "$name",
                            "2": "$name",
                            "3": ""
                        }
                    },
                    "opacity": {
                        "default": 0,
                        "feature_key": "Zoom Visibility",
                        "categories": {
                            "1": 1,
                            "2": 1,
                            "3": 1
                        }
                    }
                },
                "-3": {
                    "opacity": {
                        "default": 0,
                        "feature_key": "Zoom Visibility",
                        "categories": {
                            "1": 1,
                            "2": 1,
                            "3": 1
                        }
                    }
                },
                "-1": {
                    "opacity": 1
                }
            }
        }
    ],
    "features": [build_props(d) for d in data],
}
json.dump(overlay, sys.stdout, indent=4)
