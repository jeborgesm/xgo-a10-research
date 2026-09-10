#!/usr/bin/env python3
"""Build Arcade Test10 from golden Test08.

No firmware changes. Adds the stock XGO Foldername.ini with active section
count changed from 11 to 12, plus Resources/None and Pac-Man.zfb.
"""
import argparse, hashlib, struct, zipfile
from pathlib import Path
BASE_SHA='9c66fd727a2f894ad692b4868ba8bcee3daf2ff81b4d7eced539f80f2fd2e61e'
OUT_SHA='1a55e95702c225788cc1ed3e14a6dca294f2d30c75c3b6e3681dbc4e24e9f759'
OUT_SIZE=4921962
FOLDER_SHA='28ea468c2321f49b115be41e36ecab49b017a838f18502f7308ec52039faa2df'
STOCK_FOLDER=b'''SF2000\r\n6\r\nFFFFFF\r\nFF8000 ROMS\r\nFF8000 FC\r\nFF8000 SFC\r\nFF8000 MD\r\nFF8000 GB\r\nFF8000 GBC\r\nFF8000 GBA\r\nFF8000 ARCADE\r\nFF8000 ARCADE\r\nFF8000 ARCADE\r\nFF8000 ARCADE\r\nFF8000 ARCADE\r\n11 7 0\r\n472 144 144 208\r\n40 24\r\n'''
README=b'''XGO ARCADE TEST10 - FIFTH ARCADE SECTION / PAC-MAN PROBE\nGolden Test08 firmware is unchanged.\nFoldername.ini active-section count changes 11 -> 12, exposing the already-defined fifth ARCADE section.\nResources/None contains one entry: Pac-Man.zfb.\nARCADE/Pac-Man.zfb points to pacman.zip.\nNO ROM IS INCLUDED.\nPlace your own compatible pacman.zip at ARCADE/bin/pacman.zip.\n'''
def sha(b): return hashlib.sha256(b).hexdigest()
def zi(n):
 z=zipfile.ZipInfo(n,(2026,9,7,22,30,0)); z.compress_type=zipfile.ZIP_DEFLATED; z.create_system=3; z.external_attr=0o600<<16; return z
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--test08-zip',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
 assert sha(a.test08_zip.read_bytes())==BASE_SHA
 folder=STOCK_FOLDER.replace(b'11 7 0',b'12 7 0'); assert sha(folder)==FOLDER_SHA
 none=struct.pack('<II',1,0)+b'Pac-Man.zfb\0'
 zfb=b'\0'*(144*208*2)+b'\0'*4+b'pacman.zip\0\0'
 with zipfile.ZipFile(a.test08_zip) as zin, zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as zout:
  for info in zin.infolist(): zout.writestr(info,zin.read(info.filename))
  for n,b in [('Resources/Foldername.ini',folder),('Resources/None',none),('ARCADE/Pac-Man.zfb',zfb),('README-ARCADE-TEST10.txt',README)]: zout.writestr(zi(n),b)
 assert a.output.stat().st_size==OUT_SIZE and sha(a.output.read_bytes())==OUT_SHA
 print('zip',OUT_SIZE,OUT_SHA)
if __name__=='__main__': main()
