#!/usr/bin/env python3
from pathlib import Path

p=Path("/tmp/cps1/src/burn/drv/capcom/d_cps1.cpp")
s=p.read_text()

old='\tCps1LoadRoms(1);\n\t\n\tif (AmendProgRomCallback) AmendProgRomCallback();'
new='\tCps1LoadRoms(1);\n\treturn 1; /* TEST19: if this call returns, abort DrvInit cleanly */\n\t\n\tif (AmendProgRomCallback) AmendProgRomCallback();'

if old not in s:
    raise SystemExit("Test19 anchor not found")
s=s.replace(old,new,1)
p.write_text(s)
print("Test19 Cps1LoadRoms return probe applied")
