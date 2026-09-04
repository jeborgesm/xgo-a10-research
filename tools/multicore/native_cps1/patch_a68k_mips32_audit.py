#!/usr/bin/env python3
from pathlib import Path

p=Path("/tmp/cps1/src/cpu/a68k/mips/a68k.s")
s=p.read_text()
s=s.replace(".set arch=allegrex", ".set arch=mips32")
s=s.replace(".set nomacro", "# .set nomacro  # XGO: allow GAS pseudo expansion")
s=s.replace(".set nobopt", "# .set nobopt   # XGO: unsupported Allegrex assembler mode")
p.write_text(s)

mf=Path("/tmp/cps1/makefile.libretro")
m=mf.read_text()
old="FBA_DEFINES :=\n"
new="FBA_DEFINES := -DBUILD_A68K\n"
if old not in m:
    raise SystemExit("FBA_DEFINES anchor not found")
mf.write_text(m.replace(old,new,1))
print("patched FBA2012 for BUILD_A68K + baseline MIPS32 assembler audit")
