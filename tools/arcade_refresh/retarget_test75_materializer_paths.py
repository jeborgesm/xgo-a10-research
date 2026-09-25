#!/usr/bin/env python3
"""Patch only the BIN-closed Test75 materializer path references for Arcade.

This stage deliberately does NOT implement the post-preview ZFB/runtime-ZIP
routine. It creates a mechanically auditable parent with family import/art/meta
paths and shared /ARCADE output root.
"""
from __future__ import annotations
import hashlib,pathlib,struct,sys
from build_materializer_literal_blocks import build
from catalog_family_descriptors import FAMILIES
PARENT_SHA="8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e"
PARENT_SIZE=0x101F08
# exact low instructions whose resolved parent target was directly BIN-scanned.
TARGET_REFS={
  0x0FE8:[0x0060,0x0140],       # import; second use participates source path
  0x1003:[0x014C],              # FC root -> shared ARCADE root
  0x1011:[0x01C8,0x05BC,0x06E8,0x0710],
  0x102C:[0x01D4,0x05E0,0x06C0,0x0740,0x08D0],
  0x104A:[0x00C0],
  0x1067:[0x0158],
  0x1080:[0x0164],
}
KEY_FOR={0x0FE8:"import_dir",0x1003:"arcade_root",0x1011:"art_jpg",
         0x102C:"art_rgb",0x104A:"meta_txt",0x1067:"art_stem_jpg",
         0x1080:"art_stem_jpeg"}
def sha(b):return hashlib.sha256(b).hexdigest()
def u32(b,o):return struct.unpack_from("<I",b,o)[0]
def w32(b,o,v):struct.pack_into("<I",b,o,v&0xffffffff)
def patch_low(b,o,target):
    q=u32(b,o); assert q>>26==0x09
    lo=target&0xffff
    # All new literal addresses are 0x870011xx, so no signed carry boundary.
    w32(b,o,(q&0xffff0000)|lo)
def main():
    if len(sys.argv)!=3:raise SystemExit("retarget_test75_materializer_paths.py PARENT OUTDIR")
    parent=pathlib.Path(sys.argv[1]).read_bytes()
    assert len(parent)==PARENT_SIZE and sha(parent)==PARENT_SHA
    out=pathlib.Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
    for fam in FAMILIES:
        block,offs=build(fam)
        # build() block is rooted at +0x1100.
        offs["arcade_root"]=0x1100+len(block)
        block+=b"/mnt/sda1/ARCADE\0"
        b=bytearray(parent); assert b[0x1100:0x1100+len(block)]==b"\0"*len(block)
        b[0x1100:0x1100+len(block)]=block
        for old,refs in TARGET_REFS.items():
            target=0x87000000+offs[KEY_FOR[old]]
            for o in refs:patch_low(b,o,target)
        p=out/f"{fam.key}.refresh.paths.xgc";p.write_bytes(b)
        print(f"{fam.key} size={len(b)} sha256={sha(b)} literals={offs}")
if __name__=="__main__":main()
