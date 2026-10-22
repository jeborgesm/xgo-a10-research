#!/usr/bin/env python3
"""XGO TV mode label X -24 patch. Reproducible from approved bold-caption ZIP.
Usage: python build_tv_mode_left24.py <approved-bold-zip> <output-zip>
"""
import sys, zipfile, struct, hashlib, json
from pathlib import Path
assert len(sys.argv)==3
src,out=map(Path,sys.argv[1:3])
patch=[(0x359b88,0x2405007d,0x24050065),
       (0x35ac98,0x24050085,0x2405006d),
       (0x35acd0,0x2405008d,0x24050075)]
with zipfile.ZipFile(src) as zin:
    entries={i.filename:zin.read(i.filename) for i in zin.infolist()}
fw=bytearray(entries['bios/bisrv.asd']); prior=bytes(fw)
for offset,before,after in patch:
    assert struct.unpack_from('<I',fw,offset)[0]==before, hex(offset)
    struct.pack_into('<I',fw,offset,after)
assert struct.unpack_from('<I',fw,0xa38ab4)[0]==0x1120fd3b
poly=0x04c11db7
table=[]
for i in range(256):
    v=i<<24
    for _ in range(8): v=(((v<<1)^poly) if v&0x80000000 else v<<1)&0xffffffff
    table.append(v)
crc=0xffffffff
for c in fw[0x200:]:crc=((crc<<8)&0xffffffff)^table[((crc>>24)^c)&255]
struct.pack_into('<I',fw,0x18c,crc)
assert struct.unpack_from('<I',fw,0x184)[0]==len(fw)-512
allowed=set(range(0x18c,0x190))
for offset,_,_ in patch:allowed.update(range(offset,offset+4))
assert all(i in allowed for i,(a,b) in enumerate(zip(prior,fw)) if a!=b)
entries['bios/bisrv.asd']=bytes(fw)
entries['TV-TEXT-OFFSET-MANIFEST.json']=json.dumps({
 'base_zip_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'firmware_sha256':hashlib.sha256(fw).hexdigest(),
 'payload_crc32_mpeg2':f'{crc:08x}',
 'patches':[(hex(o),hex(a),hex(b)) for o,a,b in patch],
 'pal_submenus':'NOT FIXED',
 'status':'UNTESTED on hardware'
},indent=2).encode()
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zout:
    for name,contents in entries.items():zout.writestr(name,contents)
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('sha256',hashlib.sha256(out.read_bytes()).hexdigest())
