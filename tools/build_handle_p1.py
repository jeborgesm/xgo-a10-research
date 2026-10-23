#!/usr/bin/env python3
"""Reproduce HW-proven fixed Handle-as-P1 image. Source SHA pinned."""
import argparse,hashlib,struct
from pathlib import Path
EXPECTED='f5e2a91dced95b60ab7988952ea3a7aa1c2460c97b3644e2ea815b77b58d07aa'
OUTPUT='8a8cf7a84f7771b0fc116b80521e13d3dfbd5aace73e6053fb7494eaa7d44c4a'
HOOK=0x35d53c
CAVE=0xa398e4
def crc(data):
 c=0xffffffff
 for v in data:
  c^=v<<24
  for _ in range(8): c=((c<<1)^(0x04c11db7 if c&0x80000000 else 0))&0xffffffff
 return c
def w(b,o,v):struct.pack_into('<I',b,o,v)
def u(b,o):return struct.unpack_from('<I',b,o)[0]
def j(a):return 0x08000000|((a>>2)&0x3ffffff)
def branch(op,rs,rt,imm):return op<<26|rs<<21|rt<<16|(imm&0xffff)
def build(b):
 assert hashlib.sha256(b).hexdigest()==EXPECTED
 assert (u(b,HOOK),u(b,HOOK+4))==(0x00d43025,0x30d20020)
 assert b[CAVE:CAVE+48]==bytes(48)
 code=[branch(5,7,0,5),0,0x8f89f2d8,0x0289a025,branch(4,0,0,2),0,0x0000a021,0x00d43025,0x30d20020,j(0x80000000+HOOK+8),0]
 out=bytearray(b);w(out,HOOK,j(0x80000000+CAVE));w(out,HOOK+4,0)
 for i,v in enumerate(code):w(out,CAVE+4*i,v)
 w(out,0x184,len(out)-0x200);w(out,0x18c,crc(out[0x200:]))
 allowed=set(range(HOOK,HOOK+8))|set(range(CAVE,CAVE+44))|set(range(0x18c,0x190))
 assert all(i in allowed for i,(x,y) in enumerate(zip(b,out)) if x!=y)
 assert u(out,0x18c)==crc(out[0x200:])
 assert hashlib.sha256(out).hexdigest()==OUTPUT
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 assert a.input.resolve()!=a.output.resolve()
 result=build(a.input.read_bytes());a.output.write_bytes(result)
 print('HW-proven firmware reproduced:',OUTPUT)
