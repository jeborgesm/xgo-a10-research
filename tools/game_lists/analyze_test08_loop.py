#!/usr/bin/env python3
"""Recover high-value loop/state facts from exact Test08 MIPS scanner bytes."""
from __future__ import annotations
import argparse,struct
from pathlib import Path
BASE=0x807DAB98
REG=["zero","at","v0","v1","a0","a1","a2","a3","t0","t1","t2","t3","t4","t5","t6","t7","s0","s1","s2","s3","s4","s5","s6","s7","t8","t9","k0","k1","gp","sp","fp","ra"]
def sx(x): return x-0x10000 if x&0x8000 else x
def dec(pc,w):
 op=w>>26; rs=(w>>21)&31; rt=(w>>16)&31; rd=(w>>11)&31; imm=w&0xffff
 if op==9:return f"addiu {REG[rt]},{REG[rs]},{sx(imm)}"
 if op==15:return f"lui {REG[rt]},0x{imm:04x}"
 if op==13:return f"ori {REG[rt]},{REG[rs]},0x{imm:04x}"
 if op==35:return f"lw {REG[rt]},{sx(imm)}({REG[rs]})"
 if op==43:return f"sw {REG[rt]},{sx(imm)}({REG[rs]})"
 if op==4:return f"beq {REG[rs]},{REG[rt]},0x{pc+4+(sx(imm)<<2):08x}"
 if op==5:return f"bne {REG[rs]},{REG[rt]},0x{pc+4+(sx(imm)<<2):08x}"
 if op in (2,3):
  a=((pc+4)&0xf0000000)|((w&0x03ffffff)<<2); return ("jal" if op==3 else "j")+f" 0x{a:08x}"
 if op==0:
  fn=w&63
  if fn==0x21:return f"addu {REG[rd]},{REG[rs]},{REG[rt]}"
  if fn==8:return f"jr {REG[rs]}"
  if fn==9:return f"jalr {REG[rd]},{REG[rs]}"
 return ""
def main():
 ap=argparse.ArgumentParser();ap.add_argument("blob",type=Path);a=ap.parse_args();b=a.blob.read_bytes()
 rows=[]
 for o in range(0,len(b)-3,4):
  w=struct.unpack_from("<I",b,o)[0]; s=dec(BASE+o,w)
  if s: rows.append((BASE+o,w,s))
 # Print control flow, small constants 1..6, gp globals, and resource/count-table address material.
 for pc,w,s in rows:
  if (s.startswith(("beq","bne","j ","jal ","jalr")) or
      any(f",{n}" in s for n in range(1,7)) or "(gp)" in s or
      "0x80a3" in s.lower() or "0x80d2" in s.lower()):
   print(f"{pc:08X} {w:08X} {s}")
if __name__=="__main__":main()
