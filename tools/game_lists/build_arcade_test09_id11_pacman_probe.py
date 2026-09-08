#!/usr/bin/env python3
"""Build exact Arcade Test09 from the golden Test08 package.

No firmware changes. Adds Resources/None and a blank-thumbnail Pac-Man.zfb
reference to pacman.zip. No ROM data is included.
"""
import argparse, hashlib, struct, zipfile
from pathlib import Path

BASE_SHA='9c66fd727a2f894ad692b4868ba8bcee3daf2ff81b4d7eced539f80f2fd2e61e'
OUT_SHA='f2b6b2c127effc554f882190648f84ab7cba4a1f026a74a1ccbaf042d0768ba6'
OUT_SIZE=4922444

def sha(b): return hashlib.sha256(b).hexdigest()

def zi(name):
    z=zipfile.ZipInfo(name,(2026,9,7,21,45,0))
    z.compress_type=zipfile.ZIP_DEFLATED
    z.create_system=3
    z.external_attr=0o600<<16
    return z

README='''XGO ARCADE TEST09 — DORMANT LIST-ID 11 / PAC-MAN STOCK-DRIVER PROBE

BASELINE
--------
Golden Test08 full console scanner is preserved unchanged.
This package makes NO firmware modification.

PURPOSE
-------
Test whether the fifth stock ARCADE menu entry (list ID 11), whose three resource-table
slots all point to the literal filename Resources/None, becomes a usable native list when
that resource is supplied.

This package adds only:
  Resources/None        one-entry stock list containing Pac-Man.zfb
  ARCADE/Pac-Man.zfb    XGO arcade reference wrapper pointing to pacman.zip

The Pac-Man driver and ROM descriptors are already present in the shipped XGO FBA binary.
NO ROM IMAGE IS INCLUDED.

USER-SUPPLIED ROM
-----------------
Place your own compatible FBA 0.2.97.42-era pacman.zip in:
  ARCADE/bin/pacman.zip

Do not rename the inner ROM files. A mismatched ROM set may fail even if list-ID 11 works.

EXPECTED TEST
-------------
1. Install over the golden Test08 card.
2. Put your own compatible pacman.zip in ARCADE/bin/.
3. Browse through the five ARCADE entries.
4. The fifth ARCADE page should now contain one item: Pac-Man.zfb.
5. Launch it.

Interpretation:
- Page appears + game launches: list ID 11 is a viable general/classic Arcade page and stock Pac-Man driver works.
- Page appears + Loading/return: frontend page is viable; investigate ROM-set compatibility/stock driver launch.
- Fifth page stays empty/fails before list: list ID 11 has an additional dormant gate despite the resource table.

This probe deliberately does not alter CPS1/CPS2/NeoGeo/IGS lists and does not alter Test08 Refresh.
The generated .zfb uses a blank 144x208 RGB565 thumbnail; artwork is not part of this test.
'''.encode()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--test08-zip',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    assert sha(a.test08_zip.read_bytes())==BASE_SHA
    none=struct.pack('<II',1,0)+b'Pac-Man.zfb\0'
    zfb=b'\0'*(144*208*2)+b'\0'*4+b'pacman.zip\0\0'
    with zipfile.ZipFile(a.test08_zip) as zin, zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as zout:
        for info in zin.infolist():
            zout.writestr(info,zin.read(info.filename))
        for n,b in [('Resources/None',none),('ARCADE/Pac-Man.zfb',zfb),('README-ARCADE-TEST09.txt',README)]:
            zout.writestr(zi(n),b)
    assert a.output.stat().st_size==OUT_SIZE
    assert sha(a.output.read_bytes())==OUT_SHA
    print('zip',OUT_SIZE,OUT_SHA)

if __name__=='__main__':
    main()
