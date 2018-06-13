import re, sys, math, json
from urllib.parse import unquote

prev_ids = {f['plot_nr']: f['id'] for f in json.load(open('../../mta_plots.civmap.json'))['features']}

def get_and_convert(m):
    x = round(int(m.group(1))*.416-7400)
    z = round(int(m.group(2))*.416+2547)
    return x, z

def fn_rect(m):
    return '[%s,%s]' % get_and_convert(m)

def fn_poly(m):
    last = ',' if m.group(3) == ' ' else ']'
    return '[%s,%s]%s' % (get_and_convert(m) + (last,))

def fn_circle(m):
    x, z=get_and_convert(m)
    radius = round(int(m.group(3))*.416)
    return '"x":%s,"z":%s,"radius":%s,' % (x,z,radius)

def fn_name(m):
    pre, nr, _1, imgname, _2, name, post = m.groups()
    if not name: name = unquote(imgname.replace('_', ' '))
    fid = prev_ids.get(int(nr))
    idstr = '' if not fid else ',"id":"%s"' % fid
    return '%s%s: %s%s%s}' % (pre,nr, name,post,idstr)

print('{"features":[')
is_first_line = True
for line in sys.stdin:
    line = re.sub(r'\[([-0-9]+),([-0-9]+)\]', fn_rect, line)
    line = re.sub(r'([-0-9]+) ([-0-9]+)([ \]])', fn_poly, line)
    line = re.sub(r'"x":([-0-9]+),"z":([-0-9]+),"radius":([-0-9]+),', fn_circle, line)
    line = re.sub(r'(/%28([0-9]+)%29_?(M[Tt][Aa]_)?(\S+).png","name":")[0-9]*(: ?)?([^"]+)?(".*)}$', fn_name, line)
    line = re.sub(r'{(.+),"name":"([0-9]+): ?', r'{"plot_nr":\2,\1,"category":"house","name":"\2: ', line)
    if is_first_line: is_first_line = False
    else: print(',')
    print('    '+line[:-1], end='')
print(']}')
