#!/usr/bin/env python3
"""Reproducible XGO A10 mode text adjustment from hardware-positive PAL branch-repair ZIP.

Usage: python build_xgo_tv_final_12px.py [source-zip] [output-zip]
No changes to rendering branches, controller routing, P1/P2 underline or RGB565 resources.
"""
from pathlib import Path
import hashlib, json, struct, sys, zipfile

SOURCE=Path(sys.argv[1] if len(sys.argv)>1 else '/mnt/data/XGO_PAL_Submenu_Render_Branch_Repair_TV_Alignment_Combined_TEST.zip')
OUTPUT=Path(sys.argv[2] if len(sys.argv)>2 else '/mnt/data/XGO_PAL_Fixed_TV_Text_Final12_Bold_Handle_TEST.zip')
EXPECTED_SOURCE_ZIP_SHA='2451905dd48626524dc0303a50388170ac1ee71b7d3b29e70a45253de3e623b2'
EXPECTED_BASE_FW_SHA='efaec378c7ce6ffee8e68e42228fc05dc6514c8a67ac1ba98eb9d34b54f73481'
SHA=lambda data:hashlib.sha256(data).hexdigest()
u32=lambda data,off:struct.unpack_from('<I',data,off)[0]
put=lambda data,off,value:struct.pack_into('<I',data,off,value)
assert SHA(SOURCE.read_bytes())==EXPECTED_SOURCE_ZIP_SHA, 'Input ZIP is not HW-confirmed PAL fix'
with zipfile.ZipFile(SOURCE) as z:
    assert z.testzip() is None
    entries={n:z.read(n) for n in z.namelist()}
base=entries['bios/bisrv.asd']
assert len(base)==12768452 and SHA(base)==EXPECTED_BASE_FW_SHA
fw=bytearray(base)
# On all three TV-mode paths, X -12, Y +12 (relative to HW-positive PAL combined build).
patches=[
    (0x359B88, 0x24050059, 0x2405004D, 'TV label NTSC X 89->77'),
    (0x35AC98, 0x24050061, 0x24050055, 'TV label alternate NTSC X 97->85'),
    (0x35ACD0, 0x24050069, 0x2405005D, 'TV label PAL X 105->93'),
    (0x359B8C, 0x24060135, 0x24060141, 'TV label NTSC Y 309->321'),
    (0x35AC9C, 0x24060135, 0x24060141, 'TV label alternate NTSC Y 309->321'),
    (0x35ACD4, 0x24060135, 0x24060141, 'TV label PAL Y 309->321'),
]
for off,old,new,desc in patches:
    assert u32(fw,off)==old, f'unexpected {desc} at 0x{off:x}: 0x{u32(fw,off):08x}'
    put(fw,off,new)
# Preserve branch repair, underline and controller router byte-for-byte.
unchanged={
    0x359BA8:0x0828E296, 0x35ACB8:0x0828E296, 0x35ACF0:0x0828E296,
    0xA38EF0:0x081F6E75,0xA38AB4:0x1120FD3B,0x35D53C:0x0828E199,
}
for off,word in unchanged.items():assert u32(fw,off)==word, f'regression at {off:#x}'
# MPEG-2 nonreflected CRC32 over firmware payload from offset 0x200.
poly=0x04C11DB7
table=[]
for i in range(256):
    c=i<<24
    for _ in range(8):c=((c<<1)^poly if c&0x80000000 else c<<1)&0xFFFFFFFF
    table.append(c)
crc=0xFFFFFFFF
for b in fw[0x200:]:crc=((crc<<8)&0xFFFFFFFF)^table[((crc>>24)^b)&255]
put(fw,0x18C,crc)
assert u32(fw,0x184)==len(fw)-0x200
allowed=set(range(0x18C,0x190))
for off,*_ in patches:allowed.update(range(off,off+4))
diff=[i for i,(a,b) in enumerate(zip(base,fw)) if a!=b]
assert set(diff)<=allowed and len(diff)>6, f'Unexpected changes {diff}'
assert len(fw)==len(base)
for name,contents in entries.items():
    if name.startswith('Resources/') or name.startswith('RECOVERY/'):
        assert len(contents)>0
entries['bios/bisrv.asd']=bytes(fw)
manifest={
    'classification':'FW PATCH OFFLINE VERIFIED; label coordinates NOT HARDWARE TESTED',
    'baseline':'HW-PASS combined PAL submenu fix with approved bold captions and working Handle P1/P2',
    'source_zip':SOURCE.name,'source_zip_sha256':EXPECTED_SOURCE_ZIP_SHA,
    'source_firmware_sha256':EXPECTED_BASE_FW_SHA,
    'result_firmware_sha256':SHA(fw),'firmware_size':len(fw),
    'crc32_mpeg2':f'0x{crc:08x}',
    'changes':'ALL three dynamic TV-mode label X=-12 and Y=+12, ONLY',
    'patches':[{'offset':f'0x{off:08x}','before':f'0x{old:08x}','after':f'0x{new:08x}','reason':desc} for off,old,new,desc in patches],
    'changed_byte_offsets':[hex(x) for x in diff],
    'unchanged':['PAL rendering branch repair','Refresh/Handle menu renderer','P1/P2 routing and underline','six bold caption RGB565 Resources','fixed P1 recovery firmware'],
}
entries['TV-LABEL-FINAL12-MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
entries['README-TV-LABEL-FINAL12.txt']=(
    'XGO A10 TV LABEL ALIGNMENT REVISION (-12 X, +12 Y)\n\n'
    'Input is the USER HARDWARE-PASSED PAL + P1/P2 combined firmware.\n'
    'PAL submenu repair, Handle routing and bold resources are identical to the passed build.\n'
    'Only 6 text coordinate instructions plus LCFG CRC changed.\n'
    'Label alignment revision has NOT yet been validated on XGO hardware.\n'
    'On test SD, copy bios/ and Resources/; do NOT copy RECOVERY/.\n'
).encode()
entries['SOURCE/build_xgo_tv_final_12px.py']=Path(__file__).read_bytes()
with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name,content in entries.items():z.writestr(name,content)
with zipfile.ZipFile(OUTPUT) as z:
    assert z.testzip() is None
    assert z.read('bios/bisrv.asd')==bytes(fw)
    with zipfile.ZipFile(SOURCE) as s:
        for name in s.namelist():
            if name!='bios/bisrv.asd':assert s.read(name)==z.read(name),(name,'changed')
print('ZIP',OUTPUT)
print('ZIP SHA256',SHA(OUTPUT.read_bytes()))
print('FIRMWARE SHA256',SHA(fw))
print('CRC32/MPEG2',hex(crc))
print('DIFF OFFSET', ' '.join(hex(x) for x in diff))
