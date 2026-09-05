#!/usr/bin/env python3
from pathlib import Path
import re

p=Path("/tmp/cps1/src/cpu/a68k/mips/a68k.s")
lines=p.read_text().splitlines()
out=[]
counts={"seb":0,"seh":0,"ror":0,"rorv":0}

for line in lines:
    line=line.replace(".set arch=allegrex", ".set arch=mips32")
    line=line.replace(".set nomacro", "# .set nomacro  # XGO: baseline rewrite")
    line=line.replace(".set nobopt", "# .set nobopt   # XGO: unsupported Allegrex mode")

    m=re.match(r'^(\s*)seb\s+(\$\d+),(\$\d+)\s*(?:#.*)?$', line)
    if m:
        ind,rd,rs=m.groups()
        out.append(f"{ind}sll   {rd},{rs},24")
        out.append(f"{ind}sra   {rd},{rd},24")
        counts["seb"]+=1
        continue

    m=re.match(r'^(\s*)seh\s+(\$\d+),(\$\d+)\s*(?:#.*)?$', line)
    if m:
        ind,rd,rs=m.groups()
        out.append(f"{ind}sll   {rd},{rs},16")
        out.append(f"{ind}sra   {rd},{rd},16")
        counts["seh"]+=1
        continue

    m=re.match(r'^(\s*)ror\s+(\$2),(\$2),16\s*(?:#.*)?$', line)
    if m:
        ind,rd,rs=m.groups()
        out.append(f"{ind}srl   $1,{rs},16")
        out.append(f"{ind}sll   {rd},{rs},16")
        out.append(f"{ind}or    {rd},{rd},$1")
        counts["ror"]+=1
        continue

    m=re.match(r'^(\s*)rorv\s+(\$2),(\$2),(\$\d+)\s*(?:#.*)?$', line)
    if m:
        ind,rd,rs,sh=m.groups()
        # MIPS variable shifts mask the count to 5 bits, so -sh gives
        # (32-sh) mod 32 for the left half of rotate-right.
        out.append(f"{ind}subu  $1,$0,{sh}")
        out.append(f"{ind}sllv  $1,{rs},$1")
        out.append(f"{ind}srlv  {rd},{rs},{sh}")
        out.append(f"{ind}or    {rd},{rd},$1")
        counts["rorv"]+=1
        continue

    out.append(line)

text="\n".join(out)+"\n"

# Current m68000_intf.cpp owns and initializes a68k_memory_intf. The older
# Allegrex A68K source also allocates a private 13-word copy, causing a modern
# link collision. Convert the assembly allocation into an external reference.
old="""a68k_memory_intf:
\t.rept 13
\t\t.word 0
\t.endr
"""
if old not in text:
    raise SystemExit("a68k_memory_intf allocation not found")
text=text.replace(old, "# a68k_memory_intf storage owned by m68000_intf.cpp\n", 1)
text=text.replace(".globl a68k_memory_intf",
                  ".extern a68k_memory_intf,52", 1)

p.write_text(text)

mf=Path("/tmp/cps1/makefile.libretro")
m=mf.read_text()
old="FBA_DEFINES :=\n"
new="FBA_DEFINES := -DBUILD_A68K\n"
if old not in m:
    raise SystemExit("FBA_DEFINES anchor not found")
mf.write_text(m.replace(old,new,1))

print("patched FBA2012 for BUILD_A68K + baseline MIPS32")
print(counts)
if counts != {"seb":634,"seh":596,"ror":1,"rorv":4}:
    raise SystemExit(f"unexpected Allegrex rewrite counts: {counts}")
