#!/usr/bin/env python3
"""Build Test125 firmware dispatcher from exact HW-proven Test123.

Adds only GB/GBC/GBA command routes. Each route unwinds the selective dispatcher
frame and enters a small trampoline in free cave space. The trampoline calls the
existing HW-lineage generic external-helper runner with the system's fixed
2642-byte Stage1 /<SYSTEM>/catalog.xgc, then maps v0 exactly like the existing
selective helper paths: <0 Failed, 0 No New Games, >0 Games Updated.

FC/SFC/MD bodies, CLASSIC continuation, selector UI/B/re-entry/suppression and
Arcade's inert command remain protected.
"""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
BASE=0x80000000; INPUT_SHA="7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5"
A=0x80A38840; END=0x80A38900; TRAMP=0x80A391F8; TRAMP_END=0x80A39300
RUNNER=0x80A382E0; UPDATED=0x807DB6C0; NO_NEW=0x807DB6EC; FAILED=0x807DB718
CLASSIC=0x80A38000; MD=0x80A387AC; POLY=0x04C11DB7
PATHS={3:b"/GB/catalog.xgc\0",4:b"/GBC/catalog.xgc\0",5:b"/GBA/catalog.xgc\0"}
R={'zero':0,'v0':2,'a0':4,'a1':5,'t0':8,'t1':9,'s0':16,'s5':21,'sp':29,'ra':31}
def off(x):return x-BASE
def sha(b):return hashlib.sha256(b).hexdigest()
def iop(op,rs,rt,imm):return(op<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def jop(op,x):return(op<<26)|((x>>2)&0x03ffffff)
def lui(rt,x):return iop(15,'zero',rt,x)
def addiu(rt,rs,x):return iop(9,rs,rt,x)
def lw(rt,x,rs):return iop(35,rs,rt,x)
def slt(rd,rs,rt):return(R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|0x2a
def crc32_mpeg2(data):
 c=0xffffffff
 for x in data:
  c^=x<<24
  for _ in range(8):c=(((c<<1)^POLY)if c&0x80000000 else c<<1)&0xffffffff
 return c
class A32:
 def __init__(self,base):self.base=base;self.w=[];self.lab={};self.fix=[]
 @property
 def pc(self):return self.base+4*len(self.w)
 def L(self,n):self.lab[n]=self.pc
 def E(self,x):self.w.append(x)
 def li(self,r,x):self.E(addiu(r,'zero',x))
 def j(self,x):self.E(jop(2,x));self.E(0)
 def jal(self,x):self.E(jop(3,x));self.E(0)
 def br(self,op,rs,rt,l):self.fix.append((len(self.w),op,rs,rt,l));self.E(0);self.E(0)
 def done(self):
  for n,op,rs,rt,l in self.fix:
   pc=self.base+4*n;d=(self.lab[l]-(pc+4))//4;self.w[n]=iop(op,rs,rt,d)
  return b''.join(struct.pack('<I',x)for x in self.w)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('test123',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--manifest',type=Path);a=ap.parse_args()
 src=a.test123.read_bytes();assert sha(src)==INPUT_SHA;o=bytearray(src)
 # Protected snapshots.
 prot=[(CLASSIC,0x80A38240),(0x80A386F4,A),(0x80359AFC,0x80359BB0)]
 snaps=[bytes(o[off(x):off(y)])for x,y in prot]
 assert any(o[off(A):off(0x80A3888C)]) and not any(o[off(0x80A3888C):off(END)])
 assert not any(o[off(TRAMP):off(TRAMP_END)]),"trampoline cave not free"
 # Put path literals after trampoline code; addresses resolved after code is sized.
 d=A32(A)
 d.li('t1',2);d.br(4,'t0','t1','md')
 for cmd in (3,4,5):d.li('t1',cmd);d.br(4,'t0','t1','c'+str(cmd))
 d.li('t1',7);d.br(4,'t0','t1','classic')
 d.L('safe');d.E(lw('ra',0x1c,'sp'));d.E(lw('s0',0x18,'sp'));d.E(addiu('sp','sp',0x20));d.j(NO_NEW)
 d.L('classic');d.E(lw('ra',0x1c,'sp'));d.E(lw('s0',0x18,'sp'));d.E(addiu('sp','sp',0x20));d.li('s5',0);d.j(CLASSIC)
 for cmd in (3,4,5):
  d.L('c'+str(cmd));d.E(lw('ra',0x1c,'sp'));d.E(lw('s0',0x18,'sp'));d.E(addiu('sp','sp',0x20));d.j(TRAMP+(cmd-3)*0x40)
 d.L('md');d.j(MD)
 db=d.done();assert len(db)<=END-A;o[off(A):off(END)]=bytes(END-A);o[off(A):off(A)+len(db)]=db
 # Three fixed 0x40 trampolines. Paths are stored after code at +0xC0.
 pathbase=TRAMP+0xC0; pdata=bytearray()
 for idx,cmd in enumerate((3,4,5)):
  t=A32(TRAMP+idx*0x40);pa=pathbase+len(pdata);hi=(pa+0x8000)>>16;lo=pa&0xffff
  t.E(lui('a0',hi&0xffff));t.E(addiu('a0','a0',lo));t.li('a1',2642);t.jal(RUNNER)
  t.E(slt('t1','v0','zero'));t.br(5,'t1','zero','fail');t.br(4,'v0','zero','none');t.j(UPDATED)
  t.L('none');t.j(NO_NEW);t.L('fail');t.j(FAILED)
  tb=t.done();assert len(tb)<=0x40;o[off(t.base):off(t.base)+0x40]=tb+bytes(0x40-len(tb));pdata+=PATHS[cmd]
 assert pathbase+len(pdata)<=TRAMP_END;o[off(pathbase):off(pathbase)+len(pdata)]=pdata
 for (x,y),s in zip(prot,snaps):assert bytes(o[off(x):off(y)])==s
 struct.pack_into('<I',o,0x184,len(o)-0x200);crc=crc32_mpeg2(o[0x200:]);struct.pack_into('<I',o,0x18c,crc);assert struct.unpack_from('<I',o,0x18c)[0]==crc32_mpeg2(o[0x200:])
 a.output.write_bytes(o);m={'input_sha256':INPUT_SHA,'output_sha256':sha(o),'lcfg_crc32_mpeg2':f'0x{crc:08X}','commands':{'3':'GB /GB/catalog.xgc','4':'GBC /GBC/catalog.xgc','5':'GBA /GBA/catalog.xgc','6':'Arcade inert No New Games','7':'protected CLASSIC continuation'},'runner':'0x80A382E0','stage1_size':2642,'invariants':['exact Test123 input','FC/SFC/MD bodies unchanged','CLASSIC bootstrap unchanged','selector UI lifecycle unchanged','Arcade remains inert']}
 mp=a.manifest or a.output.with_suffix(a.output.suffix+'.manifest.json');mp.write_text(json.dumps(m,indent=2)+'\n');print('PASS',sha(o),f'CRC=0x{crc:08X}','dispatcher',len(db),'paths',len(pdata))
if __name__=='__main__':main()
