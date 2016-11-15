# -*- coding: utf-8 -*-

import re
import sys

fn = sys.argv[1]
with open(fn, 'r') as f_h:
	txt = f_h.read()

txt = txt.replace('\n', '')
s = re.search(r'\(  (.+?) \)', txt)
x = s.group(0)
#print(x)
x = x.replace('\\', '')
#print(x)
x = x.replace('  ', ' ')
#print(x)
x = x.split(' ')
#print(x)
y = list(map(lambda x: '"' + x + '"', x[1:len(x)-1]))
#print(y)
z = ' '.join(y)
print(z)
