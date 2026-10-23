#!/usr/bin/env python3
"""Rebuild XGO TV-mode text placement (-12 X, +12 Y) from HW-pass PAL ZIP.

Usage: python tools/handle/build_tv_mode_final12.py BASELINE.zip OUTPUT.zip
Only 6 coordinates + LCFG CRC are modified. Preserves approved resources,
PAL submenu branch repair, P1/P2 routing/underline, and recovery image.
"""
import hashlib, json, struct, sys, zipfile
from pathlib import Path

assert len(sys.argv)==3, "expected BASELINE.zip OUTPUT.zip"
src,out=map(Path,sys.argv[1:3])
sha=lambda b: hashlib.sha256(b).hexdigest()
assert sha(src.read_bytes())=="2451905dd48626524dc0303a50388170ac1ee71b7d3b29e70a45253de3e623b2"
with zipfile.ZipFile(src) as zin:
    assert zin.testzip() is None
    files={name:zin.read(name) for name in zin.namelist()}
base=files["bios/bisrv.asd"]
assert len(base)==12768452
assert sha(base)=="efaec378c7ce6ffee8e68e42228fc05dc6514c8a67ac1ba98eb9d34b54f73481"
fw=bytearray(base)
u32=lambda o:struct.unpack_from("<I",fw,o)[0]
patches=[
 (0x359B88,0x24050059,0x2405004D),
 (0x35AC98,0x24050061,0x24050055),
 (0x35ACD0,0x24050069,0x2405005D),
 (0x359B8C,0x24060135,0x24060141),
 (0x35AC9C,0x24060135,0x24060141),
 (0x35ACD4,0x24060135,0x24060141)]
for offset,old,new in patches:
    assert u32(offset)==old,(hex(offset),hex(u32(offset)))
    struct.pack_into("<I",fw,offset,new)
# Prove that native/PAL hook and P1/P2 mode routing remain identical.
for offset,expected in [(0x359BA8,0x0828E296),(0x35ACB8,0x0828E296),
                        (0x35ACF0,0x0828E296),(0xA38EF0,0x081F6E75),
                        (0xA38AB4,0x1120FD3B),(0x35D53C,0x0828E199)]:
    assert u32(offset)==expected
# CRC-32/MPEG-2, non-reflected, over firmware payload.
table=[]
for i in range(256):
    c=i<<24
    for _ in range(8):
        c=((c<<1)^0x04C11DB7 if c&0x80000000 else c<<1)&0xFFFFFFFF
    table.append(c)
crc=0xFFFFFFFF
for b in fw[0x200:]:
    crc=((crc<<8)&0xFFFFFFFF)^table[((crc>>24)^b)&255]
struct.pack_into("<I",fw,0x18C,crc)
assert u32(0x184)==len(fw)-0x200
assert sha(fw)=="75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b"
allowed=set(range(0x18C,0x190))
for o,_,_ in patches:allowed.update(range(o,o+4))
assert all(i in allowed for i,(a,b) in enumerate(zip(base,fw)) if a!=b)
files["bios/bisrv.asd"]=bytes(fw)
files["TV-LABEL-FINAL12-MANIFEST.json"]=json.dumps({
 "state":"offline verified, text location not hardware tested",
 "baseline_zip_sha256":sha(src.read_bytes()),
 "firmware_sha256":sha(fw),"crc32_mpeg2":f"0x{crc:08x}",
 "offset_words": [[hex(i),hex(a),hex(b)] for i,a,b in patches],
 "note":"PAL branch repair and all six approved bold RGB565 resources unchanged"
},indent=2).encode()
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name,b in files.items():z.writestr(name,b)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert z.read("bios/bisrv.asd")==bytes(fw)
print("FIRMWARE_SHA256",sha(fw))
print("ZIP_SHA256",sha(out.read_bytes()))
