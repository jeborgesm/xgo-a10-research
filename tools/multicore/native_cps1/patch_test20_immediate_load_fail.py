#!/usr/bin/env python3
from pathlib import Path

p=Path("/tmp/cps1/src/burn/drv/capcom/d_cps1.cpp")
s=p.read_text()

old='\tif (bLoad) {\n\t\tINT32 Offset = 0;'
new='\tif (bLoad) {\n\t\treturn 1; /* TEST20: immediate load-pass failure calibration */\n\t\tINT32 Offset = 0;'

if old not in s:
    raise SystemExit("Test20 anchor not found")
s=s.replace(old,new,1)
p.write_text(s)
print("Test20 immediate Cps1LoadRoms failure calibration applied")
