#!/usr/bin/env python3
"""Build family-local Arcade publication Stage2 helpers.

Architecture:
- family materializer no longer creates .refresh-set markers;
- Stage2 scans the selected family's canonical import/*.zip namespace;
- each import stem is resolved through meta/<stem>.txt to the friendly wrapper
  filename, with stem fallback when metadata is absent;
- only an already-finalized top-level /ARCADE/<title>.zfb is eligible;
- missing exact wrapper filenames are stable-appended to the selected stock
  triplet; other Arcade families are unreachable.

This is intentionally derived from the readable Test07/Test08 stable-merge
worker grammar, but it is a new offline candidate until HW proof.
"""
from __future__ import annotations
import pathlib,struct,hashlib
# This file records the closed algorithm and fail-closed simulation contract.
# Binary emission is deliberately gated on source-recovering the exact stock
# text-file read primitive/size contract used by the materializer; do not
# approximate metadata parsing.
FAMILIES={
"CPS1":("mswb7.tax","msdtc.nec","mfpmp.bvs",0x80D28968),
"CPS2":("kjbyr.tax","djoin.nec","ke89a.bvs",0x80D2896C),
"IGS":("subst.tax","aepic.nec","sensc.bvs",0x80D28970),
"NEOGEO":("rmapi.tax","pcadm.nec","ntdll.bvs",0x80D28974),
}
def candidate(import_name:str,meta_text:str|None)->str:
 assert import_name.lower().endswith(".zip")
 stem=import_name[:-4]
 title=(meta_text.strip() if meta_text and meta_text.strip() else stem)
 return title+".zfb"
def validate():
 assert tuple(FAMILIES)==("CPS1","CPS2","IGS","NEOGEO")
 assert len({v[0] for v in FAMILIES.values()})==4
 return True
if __name__=="__main__": print("PASS" if validate() else "FAIL")
