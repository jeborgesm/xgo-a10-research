#!/usr/bin/env python3
"""Rebuild the HW-proven Arcade NeoGeo Test28 stage-fit helper/package.

Input must be the exact HW-observed Test21 package. The only executable delta
is ARCADE/NEOGEO/refresh.xgc: move the canonical .refresh-set literal from the
relocated +0x3000 area into the exact-fit +0x2589 gap and repoint +0x21D8.
"""
from __future__ import annotations
import argparse, hashlib, struct, zipfile
from pathlib import Path

PARENT_ZIP_SHA="f7c46930e313d02938d67bff390874dbede5a4ae8bf5bd4130b26326f7cfb03a"
PARENT_REFRESH_SHA="b8d7e99637dea8f217e062040a4550283f7542b040232e20ad54526115a36a9f"
OUTPUT_REFRESH_SHA="0f411226154475530010071bca261c4dcc52b10fb258c043d89be029ea2ebe81"
STAGE=b"/mnt/sda1/ARCADE/NEOGEO/.refresh-set/\0"
OLD_OFF=0x3000
NEW_OFF=0x2589
REF_OFF=0x21D8
OLD_WORD=0x24C63000
NEW_WORD=0x24C62589

def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("parent",type=Path)
    ap.add_argument("output",type=Path)
    a=ap.parse_args()
    raw=a.parent.read_bytes()
    assert sha(raw)==PARENT_ZIP_SHA
    with zipfile.ZipFile(a.parent) as z:
        infos=z.infolist()
        members={i.filename:z.read(i.filename) for i in infos}
    p="ARCADE/NEOGEO/refresh.xgc"
    b=bytearray(members[p])
    assert sha(b)==PARENT_REFRESH_SHA
    assert len(STAGE)==38
    assert bytes(b[OLD_OFF:OLD_OFF+len(STAGE)])==STAGE
    assert bytes(b[NEW_OFF:NEW_OFF+len(STAGE)])==b"\0"*len(STAGE)
    assert struct.unpack_from("<I",b,REF_OFF)[0]==OLD_WORD
    b[NEW_OFF:NEW_OFF+len(STAGE)]=STAGE
    b[OLD_OFF:OLD_OFF+len(STAGE)]=b"\0"*len(STAGE)
    struct.pack_into("<I",b,REF_OFF,NEW_WORD)
    assert sha(b)==OUTPUT_REFRESH_SHA
    members[p]=bytes(b)
    with zipfile.ZipFile(a.output,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as out:
        for i in infos:
            out.writestr(i,members[i.filename])
    print("refresh",sha(members[p]))
    print("zip",sha(a.output.read_bytes()))

if __name__=="__main__":
    main()
