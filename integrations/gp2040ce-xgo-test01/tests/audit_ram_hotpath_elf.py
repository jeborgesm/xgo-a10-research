#!/usr/bin/env python3
"""Verify SRAM residency for the isolated XGO serial hotpath ELF.

Input: compiled RP2040 ELF; output: symbol placement and any direct
flash-call destinations observed in the emitted function. This is not
a cycle-accurate timing test. It never publishes a flashable UF2.
"""
from pathlib import Path
import re
import subprocess
import sys

def run(*args):
    p = subprocess.run(args, capture_output=True, text=True, check=True)
    return p.stdout

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: audit_ram_hotpath_elf.py path/to/firmware.elf")
    elf=Path(sys.argv[1])
    assert elf.is_file(), elf
    nm=run("arm-none-eabi-nm", "--defined-only", "-n", "-S", "-C", str(elf))
    regex=re.compile(r"^([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([tTwW])\s+(.+)$")
    syms=[]
    for line in nm.splitlines():
        m=regex.match(line)
        if not m: continue
        addr,size,stype,name=m.groups()
        syms.append((int(addr,16),int(size,16),stype,name))
    assert syms,"No ELF text symbols"
    for target in ("emit_frame()", "wait_clock(bool, unsigned int)",
                   "wait_data(bool, unsigned int)"):
        relevant=[s for s in syms if target in s[3]]
        if target=="emit_frame()":
            assert len(relevant)==1, f"Cannot identify unique emit_frame: {relevant}"
        if not relevant:
            print(f"{target}: optimized away / inlined")
            continue
        for addr,size,stype,name in relevant:
            isram=0x20000000<=addr<0x20050000
            print(f"{target}: {name} address=0x{addr:08x} size={size} "
                  f"section={'RAM' if isram else 'NOT_RAM'}")
            assert isram, f"Critical routine executes outside RP2040 SRAM: {name}"
    obj=run("arm-none-eabi-objdump","-d","-C",str(elf))
    header=re.compile(r"^([0-9a-fA-F]{8}) <(.+)>:$")
    call=re.compile(r"\bblx?\s+([0-9a-fA-F]+)\s+<(.+)>")
    active=None
    xip=[]
    direct_calls=[]
    for line in obj.splitlines():
        mh=header.match(line)
        if mh:
            active="emit_frame()" in mh.group(2)
            continue
        if not active: continue
        mc=call.search(line)
        if mc:
            dest=int(mc.group(1),16)
            callee=mc.group(2)
            direct_calls.append((dest,callee))
            if 0x10000000<=dest<0x11000000:
                xip.append((dest,callee))
    print(f"Direct BL/BLX calls out of SRAM emit_frame: {len(direct_calls)}")
    for addr,name in direct_calls[:30]:
        loc="XIP" if 0x10000000<=addr<0x11000000 else (
            "RAM" if 0x20000000<=addr<0x20050000 else "OTHER")
        print(f"  {loc} 0x{addr:08x} {name}")
    print(f"WARNING: direct calls into flash from emit_frame: {len(xip)}")
    # Don't declare a no-stall timing pass when source still calls flash!
    # Failing this gate will guide a narrower follow-up correction.
    assert not xip, "RAM hotpath contains XIP branch targets; not a RAM-only responder"
    print("PASS: emit_frame in SRAM, no direct branch-to-XIP detected")
    print("LIMIT: indirect calls, SRAM contention, and real XGO timing unverified")

if __name__=="__main__":
    main()
