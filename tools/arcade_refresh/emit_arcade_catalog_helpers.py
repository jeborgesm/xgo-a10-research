#!/usr/bin/env python3
"""Emit mechanically specialized Arcade catalog helpers from final GBA helper.

Only the exact HW-proven GBA helper is accepted as parent.
"""
from __future__ import annotations
import hashlib,pathlib,struct,sys
from catalog_family_descriptors import FAMILIES
from catalog_relocation import runtime,hi16,lo16

PARENT_SHA="db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6"
PARENT_SIZE=0x0A52

# (lui offset, low-half offset, target key, low op)
REFS=[
 (0x0050,0x0054,"slot0","addiu"),(0x0628,0x062C,"slot0","addiu"),
 (0x00B8,0x00BC,"slot1","addiu"),(0x0684,0x0688,"slot1","addiu"),
 (0x0120,0x0124,"slot2","addiu"),(0x06DC,0x06E0,"slot2","addiu"),
 (0x02E8,0x02F8,"root","addiu"),
]
SUFFIX_MID=0x0444
CACHE_RANGE=range(0x0730,0x073C,4)

def sha(b): return hashlib.sha256(b).hexdigest()
def rd32(b,o): return struct.unpack_from("<I",b,o)[0]
def wr32(b,o,v): struct.pack_into("<I",b,o,v&0xffffffff)

def patch_pair(b,ho,lo,target):
    oldh=rd32(b,ho); oldl=rd32(b,lo)
    rt=(oldh>>16)&31
    assert oldh>>26==0x0f
    assert (oldl>>26)==0x09 and ((oldl>>21)&31)==rt
    wr32(b,ho,(oldh&0xffff0000)|hi16(target))
    wr32(b,lo,(oldl&0xffff0000)|lo16(target))

def emit(parent:bytes,fam,out:pathlib.Path):
    b=bytearray(parent)
    assert b[SUFFIX_MID]==ord("g")
    b[SUFFIX_MID]=ord("f")
    for o in CACHE_RANGE: wr32(b,o,0)

    root=f"/mnt/sda1/ARCADE/{fam.key}/.refresh-set"
    strings={"slot0":fam.slot0,"slot1":fam.slot1,"slot2":fam.slot2,"root":root}
    offsets={}
    for key in ("slot0","slot1","slot2","root"):
        offsets[key]=len(b)
        b.extend(strings[key].encode("ascii")+b"\0")
    b.extend(b"rb\0wb\0")

    for ho,lo,key,kind in REFS:
        patch_pair(b,ho,lo,runtime(offsets[key]))

    # No GBA literals may remain reachable through the patched refs.
    assert b[SUFFIX_MID]==ord("f")
    out.write_bytes(b)
    return len(b),sha(b),offsets

def main():
    if len(sys.argv)!=3: raise SystemExit("usage: emit_arcade_catalog_helpers.py GBA_catalog.xgc OUTDIR")
    p=pathlib.Path(sys.argv[1]); parent=p.read_bytes()
    assert len(parent)==PARENT_SIZE
    assert sha(parent)==PARENT_SHA
    out=pathlib.Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
    for fam in FAMILIES:
        size,digest,offs=emit(parent,fam,out/f"{fam.key}.catalog.xgc")
        print(f"{fam.key} size={size} sha256={digest} literals={offs}")

if __name__=="__main__":main()
