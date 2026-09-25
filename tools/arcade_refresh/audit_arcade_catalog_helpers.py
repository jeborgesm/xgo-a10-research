#!/usr/bin/env python3
"""Independent audit of emitted Arcade catalog helpers."""
from __future__ import annotations
import hashlib,pathlib,struct,sys
from catalog_family_descriptors import FAMILIES
PARENT_SIZE=0x0A52
REFS=[(0x0050,0x0054,"slot0"),(0x0628,0x062C,"slot0"),
(0x00B8,0x00BC,"slot1"),(0x0684,0x0688,"slot1"),
(0x0120,0x0124,"slot2"),(0x06DC,0x06E0,"slot2"),
(0x02E8,0x02F8,"root")]
ALLOWED={0x0444,*range(0x0730,0x073c)}
for h,l,_ in REFS: ALLOWED.update(range(h,h+4));ALLOWED.update(range(l,l+4))
def u32(b,o):return struct.unpack_from("<I",b,o)[0]
def sx16(x):return x-0x10000 if x&0x8000 else x
def resolve(b,h,l):
    a=u32(b,h);q=u32(b,l)
    assert a>>26==0x0f and q>>26==0x09
    rt=(a>>16)&31; assert ((q>>21)&31)==rt
    return (((a&0xffff)<<16)+sx16(q&0xffff))&0xffffffff
def cstr(b,o):
    e=b.index(0,o);return b[o:e].decode("ascii")
def main():
    if len(sys.argv)!=3:raise SystemExit("audit_arcade_catalog_helpers.py PARENT DIR")
    p=pathlib.Path(sys.argv[1]).read_bytes(); d=pathlib.Path(sys.argv[2])
    for fam in FAMILIES:
        b=(d/f"{fam.key}.catalog.xgc").read_bytes()
        changed={i for i,(x,y) in enumerate(zip(p,b[:PARENT_SIZE])) if x!=y}
        assert changed<=ALLOWED,(fam.key,sorted(changed-ALLOWED))
        assert b[0x0444]==ord("f")
        assert b[0x0730:0x073c]==b"\0"*12
        expected={"slot0":fam.slot0,"slot1":fam.slot1,"slot2":fam.slot2,
          "root":f"/mnt/sda1/ARCADE/{fam.key}/.refresh-set"}
        for h,l,key in REFS:
            addr=resolve(b,h,l); assert addr>=0x87000000
            got=cstr(b,addr-0x87000000); assert got==expected[key],(fam.key,key,got)
        print(f"PASS {fam.key}: size={len(b)} changed-parent-bytes={len(changed)}")
if __name__=="__main__":main()
