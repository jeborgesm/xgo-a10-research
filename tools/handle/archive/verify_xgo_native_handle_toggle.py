#!/usr/bin/env python3
"""Independent behavioral MIPS interpreter + integrity test for XGO Handle toggle.

Does not import builder or reuse its assembler logic.
"""
import hashlib,struct,zipfile
from pathlib import Path
p=Path('/mnt/data/XGO_Native_Setup_Handle_P1_P2_Toggle_Hardware_Test.zip')
with zipfile.ZipFile(p) as z:
 f=z.read('bios/bisrv.asd');recovery=z.read('RECOVERY/bios/bisrv.asd')
assert hashlib.sha256(recovery).hexdigest()=='8a8cf7a84f7771b0fc116b80521e13d3dfbd5aace73e6053fb7494eaa7d44c4a'
assert len(f)==len(recovery)==12768452
assert struct.unpack_from('<I',f,0x184)[0]==len(f)-0x200
assert f[0xA398E4:0xA39910]==recovery[0xA398E4:0xA39910]
assert f[0xA39910:0xA39918]==b'\0'*8
assert struct.unpack_from('<I',f,0xA38660)[0]==0
assert struct.unpack_from('<I',f,0xA38684)[0]==0
assert struct.unpack_from('<I',f,0x7DBBA0)[0]==struct.unpack_from('<I',recovery,0x7DBBA0)[0]

POLY=0x04C11DB7
lut=[]
for i in range(256):
 c=i<<24
 for _ in range(8):c=((c<<1)^POLY if c&0x80000000 else c<<1)&0xffffffff
 lut.append(c)
c=0xffffffff
for octet in f[0x200:]:c=((c<<8)&0xffffffff)^lut[((c>>24)^octet)&255]
assert c==struct.unpack_from('<I',f,0x18c)[0]

MASK=0xffffffff
GP=0x80C34774
class CPU:
 def __init__(self,pc,registers=None,memory=None):
  self.pc=pc;self.reg=[0]*32;self.mem=dict(memory or {});self.steps=0;self.sh=[]
  self.reg[28]=GP
  for k,v in (registers or {}).items():self.reg[k]=v&MASK
 def read(self,addr,n=4):
  addr &= MASK
  if any((addr+j) in self.mem for j in range(n)):
   return sum(self.mem.get(addr+j,0)<<(8*j) for j in range(n))
  off=addr-0x80000000
  if 0<=off<len(f)-n+1:return int.from_bytes(f[off:off+n],'little')
  return 0
 def write(self,addr,v,n):
  addr &= MASK
  for j in range(n):self.mem[addr+j]=(v>>(8*j))&255
  if n==2:self.sh.append((addr,v&65535))
 def execute(self,pc,delay=False):
  w=self.read(pc);op=w>>26;rs=(w>>21)&31;rt=(w>>16)&31;rd=(w>>11)&31;sh=(w>>6)&31;fn=w&63
  imm=w&65535;sim=imm-65536 if imm&32768 else imm
  a=self.reg[rs];v=self.reg[rt];dest=None
  if op==0:
   if fn==0:self.reg[rd]=(v<<sh)&MASK
   elif fn==0x21:self.reg[rd]=(a+v)&MASK
   elif fn==0x23:self.reg[rd]=(a-v)&MASK
   elif fn==0x25:self.reg[rd]=a|v
   else:raise AssertionError(f'unsupported R {pc:#x} {w:#x}')
  elif op==2:dest=((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)
  elif op==4:
   if a==v:dest=(pc+4+sim*4)&MASK
  elif op==5:
   if a!=v:dest=(pc+4+sim*4)&MASK
  elif op==9:self.reg[rt]=(a+sim)&MASK
  elif op==11:self.reg[rt]=1 if a<(imm if imm>=0 else imm) else 0
  elif op==12:self.reg[rt]=a&imm
  elif op==13:self.reg[rt]=a|imm
  elif op==14:self.reg[rt]=a^imm
  elif op==15:self.reg[rt]=imm<<16
  elif op==35:self.reg[rt]=self.read((a+sim)&MASK)
  elif op==43:self.write((a+sim)&MASK,v,4)
  elif op==41:self.write((a+sim)&MASK,v,2)
  else:raise AssertionError(f'unsupported op {pc:#x} {w:#x}')
  self.reg[0]=0
  if delay and dest is not None:raise AssertionError('branch in delay slot')
  return dest
 def run(self,stop,maxsteps=1000):
  for _ in range(maxsteps):
   if self.pc==stop:return self
   old=self.pc;dest=self.execute(old);self.steps+=1
   if dest is not None:
    self.execute(old+4,delay=True);self.steps+=1;self.pc=dest
   else:self.pc=old+4
  raise AssertionError(f'runaway at {self.pc:#x} -> {stop:#x}')

MODE=0x80A39910
P2_RAW=0x80C33A4C

def mem_word(addr,val):return {addr+j:(val>>(j*8))&255 for j in range(4)}

for mode in (0,1):
 for player in (0,1):
  for p1,p2,rf in ((0x100,0x200,0x20),(0x40,0x400,0x8),(0x0,0x0,0x0),(0x12,0x80,0x200)):
   m=mem_word(MODE,mode)|mem_word(P2_RAW,p2)
   cpu=CPU(0x8035D53C,{3:0,6:rf,7:player,18:0x12345678,20:p1 if player==0 else p2,29:0x80D00000},m)
   cpu.run(0x8035D544)
   expected=rf|(p1 if player==0 else p2) if mode==0 else (rf|p1|p2 if player==0 else rf)
   assert cpu.reg[6]==expected,(mode,player,hex(cpu.reg[6]),hex(expected))
   assert cpu.reg[18]==(expected&0x20)
   assert cpu.reg[20]==(p1 if player==0 else p2) if mode==0 else cpu.reg[20]==(p1|p2 if player==0 else 0)
print('PASS: 16 MIPS input routing cases: P2 stock, P1 shared, both player iterations')

for old in (0,1):
 m=mem_word(MODE,old)
 cpu=CPU(0x80A38618,{3:4,29:0x80D00000,30:0},m).run(0x80359ABC)
 assert cpu.read(MODE)==1-old and cpu.reg[30]==1 and cpu.reg[18]==1
 assert cpu.steps<20
print('PASS: native Setup row4 toggles both directions and returns to native redraw')
for row in (0,1,5,7):
 cpu=CPU(0x80A38618,{3:row,29:0x80D00000},mem_word(MODE,0)).run(0x80356BFC)
 assert cpu.read(MODE)==0
print('PASS: other Setup row indices preserve stock fallback')
for row in range(5):
 cpu=CPU(0x80359B1C,{5:row,29:0x80D00000}).run(0x80359B3C)
 col=row if row<3 else row-2
 assert cpu.reg[10]==52+192*col and cpu.reg[31]==20+(224 if row>=3 else 0),(row,cpu.reg[10],cpu.reg[31])
print('PASS: native Setup highlight coordinates for all five rows')
for mode in (0,1):
 fb=0x90000000
 m=mem_word(MODE,mode)|mem_word(GP-5136,fb)
 cpu=CPU(0x80A37FA4,{29:0x80D00000},m).run(0x80A38F70)
 x=475 if mode else 541
 assert len(cpu.sh)==28*3,len(cpu.sh)
 for j in range(28):
  for y in (369,370,371):
   addr=fb+(y*640+x+j)*2
   assert (addr,65535) in cpu.sh,(mode,x,j,y)
print('PASS: native Setup visual status underline follows P1/P2 flag')
# Existing Refresh return path must skip new gate and land at original handler.
cpu=CPU(0x80A38FE0).run(0x80A38688)
assert cpu.steps==2
print('PASS: Refresh jump skips relocated gate with unchanged delay slot')
print('PASS: independent CRC, original fixed-P1 helper, recovery image, cave boundaries')
print('FW SHA256',hashlib.sha256(f).hexdigest())
print('ZIP SHA256',hashlib.sha256(p.read_bytes()).hexdigest())
