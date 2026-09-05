#!/usr/bin/env python3
from pathlib import Path

p=Path("/tmp/cps1/src/burn/drv/capcom/d_cps1.cpp")
s=p.read_text()

old='\t\t}\n\t\t\n\t\t// Graphics\n\t\tif (nCpsGfxLen) {'
new='\t\t}\n\t\t\n\t\treturn 1; /* TEST21: 68000 program-ROM phase completed */\n\t\t// Graphics\n\t\tif (nCpsGfxLen) {'

if old not in s:
    raise SystemExit("Test21 program-phase anchor not found")
s=s.replace(old,new,1)
p.write_text(s)
print("Test21 post-program-ROM failure probe applied")
