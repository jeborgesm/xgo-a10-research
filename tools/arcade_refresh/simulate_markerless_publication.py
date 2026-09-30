#!/usr/bin/env python3
"""Host-side gate for markerless four-family Arcade publication.

Input is an extracted physical SD root. This intentionally models only the
publication ownership transaction, not materialization or validation.
"""
from pathlib import Path
import argparse,struct
RES={"CPS1":"mswb7.tax","CPS2":"kjbyr.tax","IGS":"subst.tax","NEOGEO":"rmapi.tax"}
def parsecat(p):
 b=p.read_bytes(); n=struct.unpack_from("<I",b)[0]; offs=struct.unpack_from("<"+"I"*n,b,4); base=4+4*n
 return [b[base+o:b.index(0,base+o)].decode("latin1") for o in offs]
def candidates(root,fam):
 fd=root/"Arcade"/fam; top=root/"Arcade"; slot=set(parsecat(root/"Resources"/RES[fam]))
 out=[]
 for p in sorted((fd/"import").glob("*.zip")):
  stem=p.stem; m=fd/"meta"/(stem+".txt"); title=stem
  if m.exists():
   lines=[x.strip() for x in m.read_text(errors="replace").splitlines() if x.strip()]
   if lines:title=lines[0]
  w=title+".zfb"; out.append((stem,w,(top/w).is_file(),w in slot))
 return out
def main():
 a=argparse.ArgumentParser();a.add_argument("root",type=Path);x=a.parse_args()
 for f in RES:
  c=candidates(x.root,f); miss=[w for _,w,e,i in c if e and not i]
  print(f,c,"publish",miss)
if __name__=="__main__":main()
