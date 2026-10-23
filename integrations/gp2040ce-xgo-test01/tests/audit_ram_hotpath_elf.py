#!/usr/bin/env python3
"""Audit the *linked* RP2040 SRAM responder and transitive atomic veneers.

Earlier audits only classified direct BL destinations and erroneously
counted RAM linker veneers as terminal RAM functions. This revision
resolves every *_veneer call target to its actual linked symbol and fails
closed if that destination is XIP or cannot be established.

Run: python3 integrations/gp2040ce-xgo-test01/tests/audit_ram_hotpath_elf.py FILE.elf

Limit: Does not establish physical timing, indirect-call destinations,
cache state, or full transitive call-graph residency.
"""
from pathlib import Path
import re
import subprocess
import sys

def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout

def zone(addr):
    if 0x10000000 <= addr < 0x11000000:
        return "XIP"
    if 0x20000000 <= addr < 0x20042000:
        return "SRAM"
    if 0x00000000 <= addr < 0x00010000:
        return "ROM"
    return "OTHER"

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: audit_ram_hotpath_elf.py path/to/firmware.elf")
    elf=Path(sys.argv[1])
    assert elf.is_file(), elf

    nm=run("arm-none-eabi-nm","--defined-only","-n","-S","-C",str(elf))
    sym_re=re.compile(r"^([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([tTwW])\s+(.+)$")
    syms=[]
    for line in nm.splitlines():
        m=sym_re.match(line)
        if m:
            addr,size,kind,name=m.groups()
            syms.append((int(addr,16),int(size,16),kind,name))
    assert syms, "No ELF text symbols"
    lookup={}
    for addr,size,_,name in syms:
        lookup.setdefault(name,[]).append((addr,size))

    # SRAM source locations are necessary but NOT sufficient.
    critical=("emit_frame()", "wait_clock(bool, unsigned int)",
              "wait_data(bool, unsigned int)")
    for target in critical:
        relevant=[s for s in syms if target in s[3] and "_veneer" not in s[3]]
        if target=="emit_frame()":
            assert len(relevant)==1, f"Need exactly one emit_frame symbol: {relevant}"
        if not relevant:
            print(f"{target}: inlined or optimized away")
        for addr,size,_,name in relevant:
            print(f"{name}: 0x{addr:08x} size={size} zone={zone(addr)}")
            assert zone(addr)=="SRAM", f"Critical routine not SRAM-resident: {name}"

    obj=run("arm-none-eabi-objdump","-d","-C",str(elf))
    header=re.compile(r"^([0-9a-fA-F]{8}) <(.+)>:$")
    branch=re.compile(r"\bblx?\s+([0-9a-fA-F]+)\s+<(.+?)>")
    active=False
    links=[]
    for line in obj.splitlines():
        h=header.match(line)
        if h:
            active=("emit_frame()" in h.group(2)
                    and "_veneer" not in h.group(2))
            continue
        if active:
            b=branch.search(line)
            if b:
                links.append((int(b.group(1),16),b.group(2).split("+")[0]))

    print(f"emit_frame direct BL/BLX count={len(links)}")
    violations=[]
    veneers=0
    for addr,name in links:
        loc=zone(addr)
        if loc=="XIP":
            violations.append(f"direct XIP 0x{addr:08x} {name}")
        if name.endswith("_veneer"):
            veneers+=1
            raw=name[:-len("_veneer")]
            candidates=[raw]
            if raw.startswith("____"):
                candidates.append(raw[2:])
            targets=[]
            for candidate in candidates:
                targets.extend((a,candidate) for a,_ in lookup.get(candidate,[]))
            # A veneer in SRAM often jumps through an absolute literal into
            # a flash helper. The veneer address alone is *not* proof of RAM.
            if len(targets)!=1:
                violations.append(f"unresolved veneer 0x{addr:08x} {name}: {targets}")
                print(f"VENEER {name} RAM={loc}; TARGET UNRESOLVED {targets}")
            else:
                target,real=targets[0]
                print(f"VENEER {name} 0x{addr:08x} -> {real} "
                      f"0x{target:08x} ({zone(target)})")
                if zone(target)!="SRAM":
                    violations.append(f"veneer {name} points to "
                                      f"{real} at 0x{target:08x} ({zone(target)})")
        elif name.startswith("__atomic_"):
            print(f"ATOMIC DIRECT {name} 0x{addr:08x} {loc}")
    print(f"Observed {veneers} direct veneer calls, "
          f"{len(violations)} non-SRAM/unresolved destinations")
    for issue in violations:
        print("BLOCKER:",issue)
    assert not violations, (
        "SRAM emit_frame has flash-backed or unresolved calls; "
        "relocating emit_frame alone is insufficient")
    print("PASS: audited SRAM emit_frame call sites and linker veneers")
    print("LIMIT: indirect calls, other transitive helper branches and hardware timing OPEN")

if __name__=="__main__":
    main()
