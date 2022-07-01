#!/usr/bin/env python

import sys
import gzip

table = {
        'A':'A', 'B':'B', 'C':'C', 'D':'D', 'E':'E', 'F':'F', 'G':'G', 'H':'H', 'I':'I', 'J':'J', 'K':'K', 'L':'L', 'M':'M', 'N':'N', 'O':'O', 'P':'P', 'Q':'Q', 'R':'R', 'S':'S', 'T':'T', 'U':'U', 'V':'V', 'W':'W', 'X':'X', 'Y':'Y', 'Z':'Z',
        'a':'a', 'b':'b', 'c':'c', 'd':'d', 'e':'e', 'f':'f', 'g':'g', 'h':'h', 'i':'i', 'j':'j', 'k':'k', 'l':'l', 'm':'m', 'n':'n', 'o':'o', 'p':'p', 'q':'q', 'r':'r', 's':'s', 't':'t', 'u':'u', 'v':'v', 'w':'w', 'x':'x', 'y':'y', 'z':'z',
        '1':'1', '2':'2', '3':'3', '4':'4', '5':'5', '6':'6', '7':'7', '8':'8', '9':'9'
}

def gzopen(name, mode="rt"):
    if (name.endswith(".gz")):
        return gzip.open(name, mode)
    else:
        return open(name, mode)

for i in range(2, len(sys.argv)):
    k = sys.argv[i][0]
    v = sys.argv[i][1]
    if k in table:
        table[k] = v
    else:
        print("Unknown chain identifier in the arguments!!")
        exit(0)

with gzopen(sys.argv[1], 'rt') as f:
    lines = f.readlines()

results = []
for line in lines:
    if line.startswith('ATOM'):
        temp = list(line)
        try:
            temp[ 21 ] = table[ temp[21] ]
            results.append( ''.join(temp) )
        except KeyError:
            print("Unknown chain identifier in the ATOM line!!")
            exit(0)
    elif line.startswith('SSBOND'):
        temp = list(line)
        try:
            temp[ 15 ] = table[ temp[15] ]
            temp[ 29 ] = table[ temp[29] ]
            results.append( ''.join(temp) )
        except KeyError:
            print("Unknown chain identifier in the SSBOND line!!")
            exit(0)
    else:
        results.append ( line )

with open(sys.argv[1].rstrip("gz").rstrip(".").rstrip("pdb").rstrip(".") + '_chainchanged.pdb', 'w') as fout:
    for line in results:
        fout.write( line )
