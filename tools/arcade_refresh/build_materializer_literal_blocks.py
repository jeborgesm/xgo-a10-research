#!/usr/bin/env python3
"""Generate family-specific Arcade materializer literal blocks.

These blocks live in the Test75 pre-decoder zero region; this tool deliberately
does not patch executable references yet.
"""
from __future__ import annotations
import pathlib,sys
from catalog_family_descriptors import FAMILIES
BASE_OFF=0x1100
FIELDS=("import_dir","family_root","art_jpg","art_rgb","meta_txt","art_stem_jpg",
        "art_stem_jpeg","runtime_fmt","zfb_fmt","stage_dir","stage_fmt")
def strings(f):
    root=f"/mnt/sda1/ARCADE/{f.key}"
    return {
      "import_dir":root+"/import",
      "family_root":root,
      "art_jpg":root+"/art/.xgo.jpg",
      "art_rgb":root+"/art/.xgo.rgb565",
      "meta_txt":root+"/meta/%s.txt",
      "art_stem_jpg":root+"/art/%s.jpg",
      "art_stem_jpeg":root+"/art/%s.jpeg",
      "runtime_fmt":"/mnt/sda1/ARCADE/bin/%s",
      "zfb_fmt":"/mnt/sda1/ARCADE/%s",
      "stage_dir":root+"/.refresh-set",
      "stage_fmt":root+"/.refresh-set/%s",
    }
def build(f):
    b=bytearray(); offsets={}
    for k in FIELDS:
        offsets[k]=BASE_OFF+len(b);b.extend(strings(f)[k].encode("ascii")+b"\0")
    return bytes(b),offsets
def main():
    if len(sys.argv)!=2:raise SystemExit("usage: build_materializer_literal_blocks.py OUTDIR")
    out=pathlib.Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
    for f in FAMILIES:
        b,o=build(f);(out/f"{f.key}.literals.bin").write_bytes(b)
        print(f.key,len(b),{k:hex(v) for k,v in o.items()})
if __name__=="__main__":main()
