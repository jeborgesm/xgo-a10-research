#!/usr/bin/env python3
"""Build Test125 firmware dispatch from exact HW-proven Test123.

Commands 3/4/5 each invoke exactly one 2642-byte external Stage1 through the
existing generic runner. Stage1 then loads the 7000-byte source-built Stage2.
Command 6 remains inert; command 7 preserves Test123 CLASSIC continuation.
"""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
BASE=0x80000000
INPUT_SHA="7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5"
POLY=0x04C11DB7; EXT=0x80A38840; EXT_END=0x80A38900
ADAPTER=0x80A3904C; PATH_LIMIT=0x80A391F8
RUNNER=0x80A382E0; MD=0x80A387AC; CLASSIC=0x80A38000
NO_NEW=0x807DB6EC; FAILED=0x807DB718; FINISH=0x80A38808
PATHS=[b"/mnt/sda1/GB/catalog.xgc\0",b"/mnt/sda1/GBC/catalog.xgc\0",b"/mnt/sda1/GBA/catalog.xgc\0"]
def off(a):return a-BASE
def sha(b):return hashlib.sha256(b).hexdigest()
def iop(op,rs,rt,imm):return(op<<26)|(rs<<21)|(rt<<16)|(imm&0xffff)
def rtype(rs,rt,rd,fn):return(rs<<21)|(rt<<16)|(rd<<11)|fn
def jop(op,a):return(op<<26)|((a>>2)&0x03ffffff)
def crc(data):
 c=0xffffffff
 for x in data:
  c^=x<<24
  for _ in range(8):c=(((c<<1)^POLY) if c&0x80000000 else c<<1)&0xffffffff
 return c
def main():
 ap=argparse.ArgumentParser();ap.add_argument("test123",type=Path);ap.add_argument("output",type=Path);ap.add_argument("--manifest",type=Path);a=ap.parse_args()
 src=a.test123.read_bytes()
 if sha(src)!=INPUT_SHA:raise SystemExit("FAIL exact Test123 required")
 o=bytearray(src)
 if any(o[off(0x80A3888C):off(EXT_END)]):raise SystemExit("FAIL Test123 extension tail not free")
 if any(o[off(ADAPTER):off(PATH_LIMIT)]):raise SystemExit("FAIL post-suppression tail not free")
 protected={
  "classic":bytes(o[off(0x80A38000):off(0x80A38240)]),
  "stock_bodies":bytes(o[off(0x80A386F4):off(EXT)]),
  "selector":bytes(o[off(0x80A389C0):off(ADAPTER)]),
 }
 # Build adapter first; path literals follow it in the same verified zero tail.
 ptr=[]
 # compact command adapter. t0=8 command, t1=9, t2=10, a0=4,a1=5,s0=16,s5=21,sp=29,ra=31
 W=[];L={};F=[]
 def label(n):L[n]=ADAPTER+4*len(W)
 def emit(x):W.append(x)
 def li(r,v):emit(iop(9,0,r,v))
 def nop():emit(0)
 def j(x):emit(jop(2,x));nop()
 def jal(x):emit(jop(3,x));nop()
 def br(op,rs,rt,l):F.append((len(W),op,rs,rt,l));emit(0);nop()
 def lw(rt,x,rs):emit(iop(35,rs,rt,x))
 def unwind():lw(31,0x1c,29);lw(16,0x18,29);emit(iop(9,29,29,0x20))
 li(9,2);br(4,8,9,"md");li(9,7);br(4,8,9,"classic");li(9,6);br(4,8,9,"safe")
 # command 3..5: select path by three short branches, then shared runner.
 li(9,3);br(4,8,9,"gb");li(9,4);br(4,8,9,"gbc");li(9,5);br(4,8,9,"gba");F.append((len(W),2,0,0,"safe"));emit(0);nop()
 for n in ("gb","gbc","gba"):
  label(n);emit(0);emit(0) # path LUI/ADDIU resolved after adapter size is known
  F.append((len(W),2,0,0,"call"));emit(0);nop()
 label("call");li(5,2642);jal(RUNNER);li(9,0);emit(rtype(2,9,10,0x2A));br(5,10,0,"fail");emit(rtype(16,2,16,0x25));j(FINISH)
 label("fail");unwind();j(FAILED)
 label("safe");unwind();j(NO_NEW)
 label("classic");unwind();li(21,0);j(CLASSIC)
 label("md");j(MD)
 for idx,op,rs,rt,l in F:
  pc=ADAPTER+4*idx
  if op==2:W[idx]=jop(2,L[l])
  else:W[idx]=iop(op,rs,rt,(L[l]-(pc+4))//4)
 code_end=ADAPTER+4*len(W);p=(code_end+3)&~3
 for s in PATHS:ptr.append(p);p+=len(s)
 if p>PATH_LIMIT:raise SystemExit(f"FAIL adapter/path tail overflow {hex(p)}")
 for name,pa in zip(("gb","gbc","gba"),ptr):
  idx=(L[name]-ADAPTER)//4;hi=((pa+0x8000)>>16)&0xffff;lo=pa&0xffff
  W[idx]=iop(15,0,4,hi);W[idx+1]=iop(9,4,4,lo)
 o[off(EXT):off(EXT_END)]=bytes(EXT_END-EXT);struct.pack_into("<II",o,off(EXT),jop(2,ADAPTER),0)
 struct.pack_into("<"+"I"*len(W),o,off(ADAPTER),*W)
 for pa,s in zip(ptr,PATHS):o[off(pa):off(pa)+len(s)]=s
 if bytes(o[off(0x80A38000):off(0x80A38240)])!=protected["classic"]:raise SystemExit("FAIL CLASSIC changed")
 if bytes(o[off(0x80A386F4):off(EXT)])!=protected["stock_bodies"]:raise SystemExit("FAIL FC/SFC/MD changed")
 if bytes(o[off(0x80A389C0):off(ADAPTER)])!=protected["selector"]:raise SystemExit("FAIL selector/suppression changed")
 struct.pack_into("<I",o,0x184,len(o)-0x200);c=crc(o[0x200:]);struct.pack_into("<I",o,0x18c,c)
 if struct.unpack_from("<I",o,0x18c)[0]!=crc(o[0x200:]):raise SystemExit("FAIL reseal")
 a.output.write_bytes(o)
 m={"input_sha256":INPUT_SHA,"output_sha256":sha(o),"lcfg_crc32_mpeg2":f"0x{c:08X}","adapter_bytes":4*len(W),
 "paths":{k:f"0x{v:08X}" for k,v in zip(("GB","GBC","GBA"),ptr)},
 "commands":{"3":"GB catalog.xgc","4":"GBC catalog.xgc","5":"GBA catalog.xgc","6":"inert No New Games","7":"Test123 CLASSIC"},
 "invariants":["exact Test123 input","FC/SFC/MD bodies unchanged","CLASSIC bootstrap unchanged","selector/B/re-entry/suppression unchanged"]}
 mp=a.manifest or a.output.with_suffix(a.output.suffix+".manifest.json");mp.write_text(json.dumps(m,indent=2)+"\n")
 print("PASS",sha(o),f"CRC=0x{c:08X}","adapter",4*len(W),"path_end",hex(p))
if __name__=="__main__":main()
