#!/usr/bin/env python3
"""Build specification for four Arcade catalog helpers.

Parent is the exact HW-proven final GBA catalog helper:
db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6

This script intentionally requires the parent binary as input.  It will not
silently reconstruct it.
"""
from __future__ import annotations
import hashlib, pathlib, sys
from catalog_family_descriptors import FAMILIES

PARENT_SHA="db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6"
PARENT_SIZE=2642

# BIN-closed literal offsets in final GBA helper.
SLOT0_OFF=0x09E4
SLOT1_OFF=0x0A02
SLOT2_OFF=0x0A20
ROOT_OFF =0x0A3E

# GBA discovery predicate immediate locations.
SUFFIX_DOT=0x03E4
SUFFIX_Z  =0x0414
SUFFIX_MID=0x0444
SUFFIX_END=0x0470

def sha(b): return hashlib.sha256(b).hexdigest()

def require_parent(p: pathlib.Path) -> bytearray:
    b=bytearray(p.read_bytes())
    assert len(b)==PARENT_SIZE, (len(b),PARENT_SIZE)
    assert sha(b)==PARENT_SHA, sha(b)
    return b

def put_cstr(buf, off, text, capacity):
    raw=text.encode("ascii")+b"\0"
    if len(raw)>capacity:
        raise ValueError((hex(off),text,len(raw),capacity))
    buf[off:off+capacity]=raw+b"\0"*(capacity-len(raw))

def audit_suffix(buf):
    # immediate low byte in little-endian addiu/ori words
    assert buf[SUFFIX_DOT]==0x2E
    assert buf[SUFFIX_Z]==ord("z")
    assert buf[SUFFIX_MID]==ord("g")
    assert buf[SUFFIX_END]==ord("b")

def main():
    if len(sys.argv)!=3:
        raise SystemExit("usage: build_arcade_catalog_helpers.py GBA_catalog.xgc OUTDIR")
    parent=require_parent(pathlib.Path(sys.argv[1]))
    audit_suffix(parent)
    out=pathlib.Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)

    # Literal capacities are defined by the next known literal boundary.
    caps=(SLOT1_OFF-SLOT0_OFF,SLOT2_OFF-SLOT1_OFF,ROOT_OFF-SLOT2_OFF)
    for fam in FAMILIES:
        b=bytearray(parent)
        put_cstr(b,SLOT0_OFF,fam.slot0,caps[0])
        put_cstr(b,SLOT1_OFF,fam.slot1,caps[1])
        put_cstr(b,SLOT2_OFF,fam.slot2,caps[2])
        # Root needs relocation: family staging paths do not fit the original
        # tail literal slot. Refuse to emit an unsafe partial patch.
        raise RuntimeError(
          f"{fam.key}: root {fam.manifest.rsplit('/',1)[0]+'/.refresh-set'} "
          "requires literal relocation; builder intentionally stops before emission")

if __name__=="__main__": main()
