#!/usr/bin/env python3
"""Propagate HW-proven Test11 dynamic preflight/materializer to all Arcade families.

This deliberately changes no validator policy and performs no cleanup.  It
specializes only family identity and family-local import/art/meta/staging paths.
"""
from __future__ import annotations
import hashlib,pathlib,struct,sys
PARENT_SHA="5a3abb3cfe9841fc761f7778ae0b9cfc53afdd335d5f6393dc326e18e233549d"
FAMS=("CPS1","CPS2","IGS","NEOGEO")
SLOTS=((0x1200,0x20,"/mnt/sda1/ARCADE/{f}/import"),
       (0x1280,0x24,"/mnt/sda1/ARCADE/{f}/meta/%s.txt"),
       (0x12A4,0x24,"/mnt/sda1/ARCADE/{f}/art/%s.jpg"),
       (0x12C8,0x24,"/mnt/sda1/ARCADE/{f}/art/%s.jpeg"),
       (0x25C8,0x38,"/mnt/sda1/ARCADE/{f}/import/"))
STAGE_REF=0x21D8
STAGE_CPS1=0x258C
STAGE_NEOGEO=0x3000
FAMILY_WORD=0x2618\nIMPORT_PREFIX_SKIP_WORD=0x0BE4\nMARKER_NAME_SOURCE_WORD=0x21F0\nMARKER_NAME_CAP_WORD=0x21F4
def sha(b):return hashlib.sha256(b).hexdigest()
def put(b,o,n,s):
 raw=s.encode()+b"\0"
 if len(raw)>n:raise ValueError((hex(o),len(raw),n,s))
 b[o:o+n]=raw+b"\0"*(n-len(raw))
def main():
 if len(sys.argv)!=3:raise SystemExit("usage: propagate_test11_four_family.py TEST11_CPS1_REFRESH.XGC OUTDIR")
 src=pathlib.Path(sys.argv[1]).read_bytes()
 if sha(src)!=PARENT_SHA:raise SystemExit("refusing non-Test11 HW-PASS parent")
 out=pathlib.Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
 for famid,f in enumerate(FAMS):
  b=bytearray(src)
  for o,n,t in SLOTS:put(b,o,n,t.format(f=f))
  stage=f"/mnt/sda1/ARCADE/{f}/.refresh-set/"
  if f=="NEOGEO":
   if any(b[STAGE_NEOGEO:STAGE_NEOGEO+len(stage)+1]):raise SystemExit("NeoGeo relocation cave not zero")
   put(b,STAGE_NEOGEO,len(stage)+1,stage)
   w=struct.unpack_from("<I",b,STAGE_REF)[0]
   if (w&0xffff)!=STAGE_CPS1:raise SystemExit("stage reference drift")
   struct.pack_into("<I",b,STAGE_REF,(w&0xffff0000)|STAGE_NEOGEO)
  else:put(b,STAGE_CPS1,0x24,stage)
  w=struct.unpack_from("<I",b,FAMILY_WORD)[0]
  if w!=0x00002025:raise SystemExit("dynamic family selector drift")
  if famid:\n   struct.pack_into("<I",b,FAMILY_WORD,0x24040000|famid)\n  # Original materializer skips the import-directory prefix plus slash with\n  # a compiled immediate. CPS1/CPS2 share 28+1=29; IGS and NeoGeo do not.\n  # Retarget this geometry together with the family pathname.\n  w=struct.unpack_from("<I",b,IMPORT_PREFIX_SKIP_WORD)[0]\n  if w!=0x2422001d:raise SystemExit("import-prefix skip instruction drift")\n  skip=len(f"/mnt/sda1/ARCADE/{f}/import/")\n  struct.pack_into("<I",b,IMPORT_PREFIX_SKIP_WORD,(w&0xffff0000)|skip)
  # The finalizer must keep ROM shortname identity for import/bin ZIP paths,
  # but the publication marker must name the actual enriched outer wrapper.
  # The display-title buffer is already built at 0x87600400. The append helper
  # at 0x87002398 preserves a1, so its prior 0x140 capacity remains live while
  # these two words retarget only a2 from s0 (stem) to the display-title buffer.
  if struct.unpack_from("<I",b,MARKER_NAME_SOURCE_WORD)[0]!=0x02003025:raise SystemExit("marker source instruction drift")
  if struct.unpack_from("<I",b,MARKER_NAME_CAP_WORD)[0]!=0x24050140:raise SystemExit("marker capacity instruction drift")
  struct.pack_into("<I",b,MARKER_NAME_SOURCE_WORD,0x3C068760) # lui a2,0x8760
  struct.pack_into("<I",b,MARKER_NAME_CAP_WORD,0x24C60400)    # addiu a2,a2,0x400
  p=out/f/"refresh.xgc";p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  print(f,sha(b),len(b))
if __name__=="__main__":main()
