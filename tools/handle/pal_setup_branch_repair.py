#!/usr/bin/env python3
"""Rebuild the PAL Setup first-stage branch repair from approved TV-left24 ZIP."""
import sys, struct, hashlib, json, zipfile
from pathlib import Path
if len(sys.argv)!=3:
    raise SystemExit("usage: python pal_setup_branch_repair.py APPROVED_SOURCE.zip OUTPUT.zip")
src,out=map(Path,sys.argv[1:3])
with zipfile.ZipFile(src) as z:
    files={n:z.read(n) for n in z.namelist()}
fw=bytearray(files["bios/bisrv.asd"])
assert hashlib.sha256(fw).hexdigest()=="5dadf691ad812e952ef58e07a0f5cc9b183a30adf9de11e2ffc0473056a81654"
u32=lambda off:struct.unpack_from("<I",fw,off)[0]
patches=[
 (0x35acb8,0x081f6e75,0x0828e296),
 (0x35acf0,0x081f6e75,0x0828e296),
 (0x359b88,0x24050065,0x24050059),
 (0x35ac98,0x2405006d,0x24050061),
 (0x35acd0,0x24050075,0x24050069),
 (0x359b8c,0x24060129,0x24060135),
 (0x35ac9c,0x24060129,0x24060135),
 (0x35acd4,0x24060129,0x24060135),
]
assert u32(0x359ba8)==0x0828e296 and u32(0xa38ef0)==0x081f6e75
assert u32(0xa38ab4)==0x1120fd3b and u32(0x35d53c)==0x0828e199
for off,before,after in patches:
    assert u32(off)==before,(hex(off),hex(u32(off)),hex(before))
    struct.pack_into("<I",fw,off,after)
t=[]
for k in range(256):
    c=k<<24
    for j in range(8):
        c=((c<<1)^0x04c11db7 if c&0x80000000 else c<<1)&0xffffffff
    t.append(c)
crc=0xffffffff
for byte in fw[0x200:]:
    crc=((crc<<8)&0xffffffff)^t[((crc>>24)^byte)&255]
struct.pack_into("<I",fw,0x18c,crc)
assert u32(0x184)==len(fw)-0x200
files["bios/bisrv.asd"]=bytes(fw)
files["PAL-REPAIR-MANIFEST.json"]=json.dumps({"classification":"hardware UNTESTED",
 "base_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
 "firmware_sha256":hashlib.sha256(fw).hexdigest(),
 "crc_mpeg2":hex(crc),"patches":[list(map(hex,x)) for x in patches],
 "reason":"PAL alternatives bypassed stage 1, jumping straight to stage 2"}).encode()
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for name,data in files.items():z.writestr(name,data)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
print("ZIP_SHA256",hashlib.sha256(out.read_bytes()).hexdigest())
