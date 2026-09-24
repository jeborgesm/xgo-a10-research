#!/usr/bin/env python3
"""Add GB native scanner stage to the exact current HW-booting firmware.

Parent SHA256:
9d9030b1d4218561e8c042d406cb035bf8679b15166dcdedd601299429639acb

The parent already routes command 3 to 0x80A39050 and runs the proven external
GB materializer. It then exits materializer-only at 0x80A3907C.

This patch preserves that materializer call and changes only the post-success
stage to invoke stock native scanner 0x807DAE4C(a0=3), aggregate its return,
and use the existing Refresh failure/status paths.
"""
from pathlib import Path
import argparse,hashlib,struct
BASE=0x80000000
INPUT_SHA="9d9030b1d4218561e8c042d406cb035bf8679b15166dcdedd601299429639acb"
OUTPUT_SHA="32bf98353533a4cb256eb4181cc9184d9ddab7a6edf48422665c7d14b853c1d4"
EXPECTED_CRC=0x05655912
HEADER=0x200; SIZE_OFF=0x184; CRC_OFF=0x18C; POLY=0x04C11DB7
def sha(x): return hashlib.sha256(x).hexdigest()
def off(a): return a-BASE
def jop(a): return (2<<26)|((a>>2)&0x03ffffff)
def jalop(a): return (3<<26)|((a>>2)&0x03ffffff)
def iop(op,rs,rt,imm): return (op<<26)|(rs<<21)|(rt<<16)|(imm&0xffff)
def rop(rs,rt,rd,sh,fun): return (rs<<21)|(rt<<16)|(rd<<11)|(sh<<6)|fun
def br(op,rs,rt,pc,target): return iop(op,rs,rt,(target-(pc+4))//4)
def crc32m(d):
 c=0xffffffff
 for x in d:
  c^=x<<24
  for _ in range(8): c=(((c<<1)^POLY) if c&0x80000000 else c<<1)&0xffffffff
 return c
def main():
 ap=argparse.ArgumentParser();ap.add_argument("input",type=Path);ap.add_argument("output",type=Path);a=ap.parse_args()
 src=a.input.read_bytes()
 if sha(src)!=INPUT_SHA: raise SystemExit("FAIL wrong parent")
 o=bytearray(src)
 def word(x): return struct.unpack_from("<I",o,off(x))[0]
 def put(x,v): struct.pack_into("<I",o,off(x),v)
 # Assert exact current GB materializer-only exit and free/reclaimable tail.
 if word(0x80A3907C)!=jop(0x80A38808): raise SystemExit("FAIL GB exit mismatch")
 put(0x80A3907C,jop(0x80A39084))
 A=0x80A39084
 code=[
  iop(9,0,4,3),jalop(0x807DAE4C),0,
  iop(9,0,8,0),rop(2,8,9,0,42),br(5,9,0,A+20,0x80A3882C),0,
  rop(16,2,16,0,37),jop(0x80A38808),0]
 for i,x in enumerate(code): put(A+4*i,x)
 struct.pack_into("<I",o,SIZE_OFF,len(o)-HEADER)
 c=crc32m(bytes(o[HEADER:]));struct.pack_into("<I",o,CRC_OFF,c)
 if c!=EXPECTED_CRC or sha(o)!=OUTPUT_SHA: raise SystemExit("FAIL final identity")
 a.output.write_bytes(o)
 print("PASS",OUTPUT_SHA,f"CRC=0x{c:08X}")
if __name__=="__main__":main()
