#!/usr/bin/env python3
"""Reproduce the exact XGO Test08 six-console scanner candidate.

This builder starts from the hardware-confirmed Test06b golden ZIP, replaces
only the proven firmware cave/status hooks with the pre-audited Test08 scanner
blob, and deliberately omits all catalog/test-ROM proof payloads from install.
"""
from __future__ import annotations
import argparse, base64, hashlib, struct, zipfile, zlib
from pathlib import Path

TEST06B_ZIP_SHA='2d859b3ca3f0644a461c197fcfe0b58f2650c26bc6a7c8d28a189da196aa1042'
TEST06B_FW_SHA='5d15cbe1cef380b3517cbd64727526e1b837df5160ba5275ccde6fec01324f4e'
TEST06B_BLOB_SHA='31590cfb05e4b02536ae288218108b066f9bf0b3d836117f2fb873d830b591bc'
TEST06B_BLOB_LEN=1370
SCANNER_SHA='a3f965d0ccabc2238da240a4b05b5f8027c968e40ede1831b51c42cff374c01d'
SCANNER_LEN=3601
EXPECTED_FW_SHA='45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444'
EXPECTED_ZIP_SHA='9c66fd727a2f894ad692b4868ba8bcee3daf2ff81b4d7eced539f80f2fd2e61e'
EXPECTED_ZIP_SIZE=4921057
BASE=0x80000000; CAVE=0x807DAB98; CAVE_LIMIT=0x807DBBA0
DISPATCH=0x80359EA8; POST_TV_HOOK=0x80359BA8; POST_TV_PAL_A_HOOK=0x8035ACB8; POST_TV_PAL_B_HOOK=0x8035ACF0
STATUS_DRAW=0x807DB7CC; POLY=0x04C11DB7
SCANNER_ZB64='''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'''
README_BYTES='''XGO GAME-LIST TEST08 — FULL CONSOLE DISCOVERY + STABLE MERGE

PROTECTED INPUT
---------------
Golden Test06b explicit Refresh UI/timed status
ZIP SHA-256      2d859b3ca3f0644a461c197fcfe0b58f2650c26bc6a7c8d28a189da196aa1042
firmware SHA-256 5d15cbe1cef380b3517cbd64727526e1b837df5160ba5275ccde6fec01324f4e

WHAT CHANGED
------------
Test08 removes Resources/refresh.bin entirely. One press of Refresh iterates:
FC -> SFC -> MD -> GB -> GBC -> GBA.

For each system it:
1. resolves the stock filename/title/search triplet from the firmware resource table;
2. scans the real system directory through the stock directory wrappers;
3. accepts that folder's wrapper extension plus native emulator-family extensions;
4. compares every discovered physical filename against slot 0;
5. preserves every existing entry/index/order;
6. collects and appends ALL missing physical filenames (up to 512 per system);
7. appends basename fallbacks to slots 1 and 2;
8. builds the complete synchronized triplet in RAM before canonical writes;
9. rewrites, fs_syncs, and invalidates count[list_id] only for changed systems;
10. continues through all six console systems and reports the aggregate result.

No ROM name, catalog count, or expected append count is hardcoded.
The install ZIP contains NO game-list catalog files and NO test ROM payloads.

The extension classifier's global system-mask side effect is saved/restored.
The golden Test06b UI resources are otherwise carried forward unchanged.

SAFETY BOUNDARY
---------------
This is the full six-console scanner candidate but is still intentionally non-transactional.
Use ONLY on the disposable clone. A power loss or write failure during the canonical
triplet rewrite can still leave one or more console catalogs inconsistent. Transaction-marker
recovery is the next safety layer after discovery/stable-merge hardware proof.

EXPECTED DISPOSABLE-CLONE TEST
------------------------------
Before installing, note the visible counts for FC/SFC/MD/GB/GBC/GBA.

First Refresh:
- must scan all six physical directories itself;
- status: Games Updated if any unindexed ROM exists in any console folder;
- every physical-but-unindexed ROM should be appended to its correct system;
- existing ordering/indices must remain unchanged.

Second Refresh:
- status: No New Games;
- no further catalog change expected.

Regression checks:
- sample old Favorites/history/save references still resolve correctly;
- Search and Chinese-mode list access remain aligned;
- newly discovered games launch from the correct emulator page;
- User Games/Language/TV System unchanged;
- timed status still expires after about three seconds;
- audio OSD / SNES / CPS1 protected behavior unchanged.

Firmware cave: 0x807dab98..0x807dbba0
scanner/status blob bytes: 3601
scanner/status blob SHA-256: a3f965d0ccabc2238da240a4b05b5f8027c968e40ede1831b51c42cff374c01d
LCFG CRC-32/MPEG-2: 0xf8cd991b
Candidate firmware SHA-256: 45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444
'''.encode()

def sha(b): return hashlib.sha256(b).hexdigest()
def j(addr): return (2<<26)|((addr>>2)&0x03ffffff)
def crc32_mpeg2(data):
    crc=0xffffffff
    for byte in data:
        crc ^= byte<<24
        for _ in range(8): crc=(((crc<<1)^POLY) if crc&0x80000000 else crc<<1)&0xffffffff
    return crc
def zi(name):
    z=zipfile.ZipInfo(name,(2026,9,7,18,55,0)); z.compress_type=zipfile.ZIP_DEFLATED; z.create_system=3; z.external_attr=0o600<<16; return z

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--test06b-zip',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    raw=args.test06b_zip.read_bytes(); assert sha(raw)==TEST06B_ZIP_SHA
    with zipfile.ZipFile(args.test06b_zip) as z: members={n:z.read(n) for n in z.namelist()}
    fw=bytearray(members['bios/bisrv.asd']); assert sha(fw)==TEST06B_FW_SHA
    assert sha(bytes(fw[CAVE-BASE:CAVE-BASE+TEST06B_BLOB_LEN]))==TEST06B_BLOB_SHA
    blob=zlib.decompress(base64.b64decode(SCANNER_ZB64)); assert len(blob)==SCANNER_LEN and sha(blob)==SCANNER_SHA
    fw[CAVE-BASE:CAVE_LIMIT-BASE]=b'\0'*(CAVE_LIMIT-CAVE); fw[CAVE-BASE:CAVE-BASE+len(blob)]=blob
    for addr,target in [(DISPATCH,CAVE),(POST_TV_HOOK,STATUS_DRAW),(POST_TV_PAL_A_HOOK,STATUS_DRAW),(POST_TV_PAL_B_HOOK,STATUS_DRAW)]: struct.pack_into('<I',fw,addr-BASE,j(target))
    crc=crc32_mpeg2(fw[0x200:]); struct.pack_into('<I',fw,0x18c,crc); assert sha(fw)==EXPECTED_FW_SHA
    proof_only={'Resources/refresh.bin','Resources/urefs.tax','Resources/adsnt.nec','Resources/xvb6c.bvs','SFC/XGO Import Test.zsf'}
    order=[n for n in members if n not in proof_only]
    with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in order:
            if n=='README-HARDWARE-TEST.txt': z.writestr(zi(n),README_BYTES)
            elif n=='bios/bisrv.asd': z.writestr(zi(n),bytes(fw))
            else: z.writestr(zi(n),members[n])
    assert args.output.stat().st_size==EXPECTED_ZIP_SIZE and sha(args.output.read_bytes())==EXPECTED_ZIP_SHA
    print('scanner',len(blob),sha(blob)); print('firmware',sha(fw)); print('zip',args.output.stat().st_size,sha(args.output.read_bytes()))
if __name__=='__main__': main()
