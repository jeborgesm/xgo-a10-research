#!/usr/bin/env python3
from pathlib import Path

p=Path("/tmp/cps1/src/burn/drv/capcom/d_cps1.cpp")
s=p.read_text()

old='\t\t\t\ti += 2;\n\t\t\t}'
new='\t\t\t\ti += 2;\n\t\t\t\tif (i == 4) return 1; /* TEST22: first two 68K ROM pairs completed */\n\t\t\t}'

if old not in s:
    raise SystemExit("Test22 pair-bisect anchor not found")
s=s.replace(old,new,1)
p.write_text(s)
print("Test22 after-two-program-pairs probe applied")
