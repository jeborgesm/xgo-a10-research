#!/usr/bin/env python3
"""XGO Setup PAL recovery candidate, from HW-approved bold-caption / -24 X package.

Target two PAL/alternate-TV exits that bypass the first-stage renderer and
rejoin the already-working NTSC Setup compositor, preserving shared second stage.
Also shift NTSC/PAL dynamic labels 12 more px left and 12 px down.

This is an OFFLINE-VALIDATED, HARDWARE-UNTESTED firmware test.
"""
import hashlib, json, struct, zipfile
from pathlib import Path

ROOT=Path('/mnt/data')
SOURCE=ROOT/'XGO_TV_Text_Left24_Bold_P1_P2_PAL_Pending_TEST.zip'
TARGET=ROOT/'XGO_PAL_Submenu_Render_Branch_Repair_TV_Alignment_Combined_TEST.zip'
U32=lambda b,o:struct.unpack_from('<I',b,o)[0]
PUT=lambda b,o,w:struct.pack_into('<I',b,o,w)
SHA=lambda b:hashlib.sha256(b).hexdigest()

# Device runtime is firmware offset + 0x80000000. MIPS J keeps high nibble.
ORIGINAL_SECOND_STAGE=0x807DB9D4
FIRST_STAGE=0x80A38A58
j=lambda addr:0x08000000|((addr>>2)&0x03ffffff)

# All three native paths share the same Setup framebuffer + text primitives.
# The NTSC path already enters FIRST_STAGE at file 0x359BA8.
# Two alternate TV-mode exits skipped it and jumped straight to second stage.
PATCHES=[
 (0x35ACB8,j(ORIGINAL_SECOND_STAGE),j(FIRST_STAGE),'TV-mode branch A enters custom first-stage renderer'),
 (0x35ACF0,j(ORIGINAL_SECOND_STAGE),j(FIRST_STAGE),'TV-mode branch B enters custom first-stage renderer'),
 (0x359B88,0x24050065,0x24050059,'NTSC label X 101->89'),
 (0x35AC98,0x2405006D,0x24050061,'NTSC alternate label X 109->97'),
 (0x35ACD0,0x24050075,0x24050069,'PAL label X 117->105'),
 (0x359B8C,0x24060129,0x24060135,'NTSC label Y 297->309'),
 (0x35AC9C,0x24060129,0x24060135,'NTSC alternate label Y 297->309'),
 (0x35ACD4,0x24060129,0x24060135,'PAL label Y 297->309'),
]

with zipfile.ZipFile(SOURCE) as zin:
 assert zin.testzip() is None
 original_items={name:zin.read(name) for name in zin.namelist()}
base=original_items['bios/bisrv.asd']
assert len(base)==12768452
assert SHA(base)=='5dadf691ad812e952ef58e07a0f5cc9b183a30adf9de11e2ffc0473056a81654'
fw=bytearray(base)
assert U32(fw,0x359BA8)==j(FIRST_STAGE),'NTSC hook not in known-good state'
assert U32(fw,0xA38EF0)==j(ORIGINAL_SECOND_STAGE),'first-stage must rejoin second-stage'
assert U32(fw,0xA38AB4)==0x1120FD3B,'P1/P2 underline hook removed'
assert U32(fw,0x35D53C)==j(0x80A38664),'controller routing unexpectedly modified'

manifest_patches=[]
for off,expected,replacement,why in PATCHES:
 observed=U32(fw,off)
 assert observed==expected,(hex(off),hex(observed),hex(expected))
 PUT(fw,off,replacement)
 manifest_patches.append({'file_offset':f'0x{off:08x}','runtime_address':f'0x{0x80000000+off:08x}',
    'before':f'0x{expected:08x}','after':f'0x{replacement:08x}','purpose':why})

# LCFG CRC32/MPEG2 from payload 0x200: (init FFFFFFFF, poly 04C11DB7).
POLY=0x04C11DB7
TABLE=[]
for i in range(256):
 c=i<<24
 for _ in range(8):c=(((c<<1)^POLY) if c&0x80000000 else c<<1)&0xffffffff
 TABLE.append(c)
crc=0xffffffff
for octet in fw[0x200:]:
 crc=((crc<<8)&0xffffffff)^TABLE[((crc>>24)^octet)&0xff]
PUT(fw,0x18c,crc)
assert U32(fw,0x184)==len(fw)-0x200
assert U32(fw,0x35ACB8)==U32(fw,0x35ACF0)==U32(fw,0x359BA8)
assert U32(fw,0xA38EF0)==j(ORIGINAL_SECOND_STAGE)
assert U32(fw,0xA38AB4)==0x1120FD3B
assert U32(fw,0x35D53C)==j(0x80A38664)

allowed=set(range(0x18c,0x190))
for off,_,_,_ in PATCHES:allowed.update(range(off,off+4))
changed=[p for p,(a,b) in enumerate(zip(base,fw)) if a!=b]
assert set(changed)<=allowed,('unexpected firmware change',changed)
assert len(fw)==len(base)

langs=('dxkgi.ctp','itiss.ers','esent.bvs','awusa.tax','vssvc.nec','vidca.bvs')
for name in langs:
 assert len(original_items['Resources/'+name])==614400
 assert original_items['Resources/'+name]==zipfile.ZipFile(SOURCE).read('Resources/'+name)

entries=dict(original_items)
entries['bios/bisrv.asd']=bytes(fw)
manifest={
 'project':'XGO A10 native Setup PAL menu compositor branch repair with TV label adjustment',
 'classification':'OFFLINE VERIFIED / HARDWARE UNTESTED',
 'source_zip':SOURCE.name,'source_sha256':SHA(SOURCE.read_bytes()),
 'firmware_sha256':SHA(fw),'firmware_size':len(fw),'crc32_mpeg2':f'0x{crc:08x}',
 'pal_hypothesis':'Two PAL/alternate TV code paths bypass custom first-stage Setup overlay, entering only second-stage. Re-route to shared first stage as NTSC already does.',
 'verified_paths':{'NTSC':'0x80359BA8 -> 0x80A38A58','other_tv_path_a':'0x8035ACB8 -> 0x80A38A58','other_tv_path_b':'0x8035ACF0 -> 0x80A38A58', 'stage1_exit':'0x80A38EF0 -> 0x807DB9D4'},
 'tv_text_adjustment':'additional left 12, down 12 relative to approved left24 ZIP',
 'controller_routing':'unchanged','p1p2_underline':'unchanged','approved_bold_setup_resources':'all six unchanged',
 'patches':manifest_patches,'changed_byte_offsets':[f'0x{x:x}' for x in changed],
 'status':'PAL fix not hardware confirmed; A/B NTSC and PAL test required'
}
entries['PAL-COMPOSITOR-BRANCH-REPAIR-MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
entries['README-PAL-BRANCH-REPAIR.txt']=(
 'XGO A10 COMBINED PAL MENU RENDER / TV MODE TEXT ALIGNMENT TEST\n\n'
 'EXPERIMENTAL. Offline verified, not yet hardware tested. Use TEST SD clone.\n'
 'PAL failure diagnosis: two alternate TV drawing branches skip first-stage compositor; now unified with NTSC entry.\n'
 'Also moves NTSC/PAL labels 12 more px left and 12 px down.\n'
 'Six user-approved bold-caption graphics remain byte-for-byte identical.\n'
 'Preserves controller toggle, P1/P2 underline, Refresh, CLASSIC and stock firmware outside the enumerated patch sites.\n\n'
 'TEST ORDER: Boot NTSC and check SETUP/REFRESH/HANDLE + controller switching.\n'
 'Select PAL, check SETUP then enter REFRESH and HANDLE and verify both menus now visible; switch back to NTSC.\n'
 'Inspect TV label placement in both output modes.\n'
 'IF BOOT/RENDER FAILS restore original SD BIOS and Resources backup.\n'
 'RECOVERY/ contains HW-proven fixed-P1 firmware; do NOT copy RECOVERY/ to SD root.\n'
 'Exact checksums and patch instructions in PAL-COMPOSITOR-BRANCH-REPAIR-MANIFEST.json\n'
 ).encode()
entries['SOURCE/build_xgo_pal_branch_restore_bundle.py']=Path(__file__).read_bytes()

with zipfile.ZipFile(TARGET,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zout:
 for name,contents in entries.items():
  zi=zipfile.ZipInfo(name,(2026,10,22,20,10,0))
  zi.compress_type=zipfile.ZIP_DEFLATED
  zi.create_system=3;zi.external_attr=0o644<<16
  zout.writestr(zi,contents)
with zipfile.ZipFile(TARGET) as z:
 assert z.testzip() is None
 assert z.read('bios/bisrv.asd')==bytes(fw)
 for name in langs:assert z.read('Resources/'+name)==original_items['Resources/'+name]
 assert z.read('RECOVERY/bios/bisrv.asd')==original_items['RECOVERY/bios/bisrv.asd']
 print('ZIP',TARGET)
 print('ZIP_BYTES',TARGET.stat().st_size)
 print('ZIP_SHA256',SHA(TARGET.read_bytes()))
 print('FW_SHA256',SHA(fw))
 print('CRC32_MPEG2',hex(crc))
 print('CHANGED_BYTES',len(changed),[hex(x) for x in changed])
 print('ALL_TESTS_PASSED')
