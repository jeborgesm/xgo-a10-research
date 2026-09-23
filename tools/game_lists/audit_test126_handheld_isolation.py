#!/usr/bin/env python3
"""Static isolation audit for corrected Test126 handheld Stage2 helpers."""
from __future__ import annotations
import argparse, struct
from pathlib import Path

SYSTEMS={
 "gb":  dict(names=0x80A3C35C,count=0x80D28964,folder=b"GB"),
 "gbc": dict(names=0x80A3C368,count=0x80D2896C,folder=b"GBC"),
 "gba": dict(names=0x80A3C374,count=0x80D28974,folder=b"GBA"),
}

def u32le_words(blob:bytes):
 return [struct.unpack_from("<I",blob,i)[0] for i in range(0,len(blob)-3,4)]

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("stage2",type=Path); a=ap.parse_args()
 for name,d in SYSTEMS.items():
  p=a.stage2/f"{name}-catalog-saf.xgc"; b=p.read_bytes(); words=u32le_words(b)
  if len(b)!=7000: raise SystemExit(f"FAIL {name}: size {len(b)}")
  # The builder emits LUI/ADDIU address loads. Decode immediate halves from
  # instruction words instead of searching arbitrary bytes.
  his=[]; los=[]
  for w in words:
   op=w>>26
   if op==0x0f: his.append(w&0xffff)          # lui
   if op in (0x09,0x0d): los.append(w&0xffff) # addiu/ori
  for key in ("names","count"):
   v=d[key]; hi=(v>>16)&0xffff; lo=v&0xffff
   if hi not in his or lo not in los:
    raise SystemExit(f"FAIL {name}: own {key} address 0x{v:08X} not encoded")
  if d["folder"]+b"\0" not in b:
   raise SystemExit(f"FAIL {name}: own folder literal absent")
  for other,od in SYSTEMS.items():
   if other!=name and od["folder"]+b"\0" in b:
    raise SystemExit(f"FAIL {name}: foreign folder literal {other} present")
  print(f"PASS {name}: names=0x{d['names']:08X} count=0x{d['count']:08X} folder={d['folder'].decode()}")
if __name__=="__main__": main()
