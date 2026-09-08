#!/usr/bin/env python3
"""Build Arcade Test09 from the exact golden Test08 package.

No firmware changes. Adds Resources/None and a blank-thumbnail Pac-Man.zfb
reference to pacman.zip. No ROM data is included.
"""
import argparse, hashlib, struct, zipfile
from pathlib import Path

BASE_SHA='9c66fd727a2f894ad692b4868ba8bcee3daf2ff81b4d7eced539f80f2fd2e61e'
OUT_SHA='f2b6b2c127effc554f882190648f84ab7cba4a1f026a74a1ccbaf042d0768ba6'

def sha(b): return hashlib.sha256(b).hexdigest()

def catalog(name):
    b=name.encode('ascii')
    return struct.pack('<II',1,0)+b+b'\0'

def zi(name):
    z=zipfile.ZipInfo(name,(2026,9,7,21,45,0))
    z.compress_type=zipfile.ZIP_DEFLATED
    z.create_system=3
    z.external_attr=0o600<<16
    return z

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--test08-zip',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    assert sha(a.test08_zip.read_bytes())==BASE_SHA
    none=catalog('Pac-Man.zfb')
    zfb=b'\0'*(144*208*2)+b'\0'*4+b'pacman.zip\0\0'
    readme=b'''XGO ARCADE TEST09 - LIST-ID 11 / PAC-MAN PROBE\n\nNo firmware modification. No ROM included.\nPlace your own compatible pacman.zip in ARCADE/bin/pacman.zip.\nThe package supplies Resources/None and ARCADE/Pac-Man.zfb only.\nBrowse the fifth ARCADE entry and attempt to launch Pac-Man.\n'''
    with zipfile.ZipFile(a.test08_zip) as zin, zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as zout:
        for info in zin.infolist():
            zout.writestr(info,zin.read(info.filename))
        for n,b in [('Resources/None',none),('ARCADE/Pac-Man.zfb',zfb),('README-ARCADE-TEST09.txt',readme)]:
            zout.writestr(zi(n),b)
    print('zip',a.output.stat().st_size,sha(a.output.read_bytes()))
if __name__=='__main__':
    main()
