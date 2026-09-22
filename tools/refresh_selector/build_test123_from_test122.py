#!/usr/bin/env python3
"""Build HW-proven Test123 CLASSIC rescue from exact HW-proven Test122.

Test123 changes only execution dispatch:
  0 -> existing FC
  1 -> existing SFC
  2 -> existing MD
  3..6 -> native No New Games (safe non-mutating placeholder)
  7 -> unwind selective-dispatch frame, s5=0, jump to preserved
       CLASSIC continuation 0x80A38000.

The CLASSIC helper is deliberately external. Canonical Test72 helper:
  /CLASSIC/refresh.xgc
  SHA256 9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

BASE=0x80000000
INPUT_SHA="6378e4a9cbf560afa53c38836826c294c9b2316310d65eb9860894c221cb2f0d"
EXPECTED_OUTPUT_SHA="7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5"
EXPECTED_CRC=0x91CA4950
CLASSIC_HELPER_SHA="9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f"
HEADER_SIZE=0x200; SIZE_OFFSET=0x184; CRC_OFFSET=0x18C; POLY=0x04C11DB7
ELSE_JUMP=0x80A386EC; EXT=0x80A38840
MD=0x80A387AC; CLASSIC=0x80A38000; NO_NEW=0x807DB6EC

def off(a): return a-BASE
def sha(b): return hashlib.sha256(b).hexdigest()
def jop(a): return (2<<26)|((a>>2)&0x03ffffff)
def iop(op,rs,rt,imm): return (op<<26)|(rs<<21)|(rt<<16)|(imm&0xffff)
def word(b,a): return struct.unpack_from("<I",b,off(a))[0]
def put(b,a,x): struct.pack_into("<I",b,off(a),x)
def crc32_mpeg2(data):
 c=0xffffffff
 for byte in data:
  c^=byte<<24
  for _ in range(8): c=(((c<<1)^POLY) if c&0x80000000 else c<<1)&0xffffffff
 return c
def reseal(b):
 struct.pack_into("<I",b,SIZE_OFFSET,len(b)-HEADER_SIZE)
 c=crc32_mpeg2(bytes(b[HEADER_SIZE:]))
 struct.pack_into("<I",b,CRC_OFFSET,c)
 return c

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("test122",type=Path); ap.add_argument("output",type=Path)
 ap.add_argument("--manifest",type=Path)
 a=ap.parse_args(); src=a.test122.read_bytes()
 if sha(src)!=INPUT_SHA: raise SystemExit("FAIL input is not exact HW-proven Test122")
 o=bytearray(src)
 if word(o,ELSE_JUMP)!=jop(MD): raise SystemExit("FAIL inherited else->MD word mismatch")
 if any(o[off(EXT):off(EXT)+0x60]): raise SystemExit("FAIL extension cave not zero/free")
 bootstrap=bytes(o[off(CLASSIC):off(0x80A38240)])
 bodies=bytes(o[off(0x80A386F4):off(EXT)])

 # t0=8 command, t1=9 scratch, s0=16, s5=21, sp=29, ra=31
 helper=[
  iop(9,0,9,2), iop(4,8,9,15), 0,       # cmd2 -> final MD jump
  iop(9,0,9,7), iop(5,8,9,7), 0,        # !=7 -> safe unwind
  iop(35,29,31,0x1c), iop(35,29,16,0x18), iop(9,29,29,0x20),
  iop(9,0,21,0), jop(CLASSIC), 0,        # cmd7 -> CLASSIC continuation
  iop(35,29,31,0x1c), iop(35,29,16,0x18), iop(9,29,29,0x20),
  jop(NO_NEW),0,                          # cmd3..6 -> native no-change
  jop(MD),0                               # cmd2 target
 ]
 put(o,ELSE_JUMP,jop(EXT))
 for i,x in enumerate(helper): put(o,EXT+4*i,x)

 if bytes(o[off(CLASSIC):off(0x80A38240)])!=bootstrap: raise SystemExit("FAIL CLASSIC bootstrap changed")
 if bytes(o[off(0x80A386F4):off(EXT)])!=bodies: raise SystemExit("FAIL FC/SFC/MD bodies changed")
 crc=reseal(o)
 calc=crc32_mpeg2(bytes(o[HEADER_SIZE:]))
 if crc!=calc or crc!=EXPECTED_CRC: raise SystemExit("FAIL CRC")
 if sha(o)!=EXPECTED_OUTPUT_SHA: raise SystemExit("FAIL final SHA")
 a.output.write_bytes(o)
 mp=a.manifest or a.output.with_suffix(a.output.suffix+".manifest.json")
 mp.write_text(json.dumps({
  "input_sha256":INPUT_SHA,"output_sha256":EXPECTED_OUTPUT_SHA,
  "lcfg_crc32_mpeg2":f"0x{crc:08X}",
  "classic_helper_sha256":CLASSIC_HELPER_SHA,
  "changes":[
   {"address":"0x80A386EC","purpose":"replace inherited else->MD with extension"},
   {"address":"0x80A38840","size":len(helper)*4,"purpose":"cmd2 MD; cmd7 CLASSIC; cmd3..6 safe native no-change"}
  ],
  "invariants":["exact Test122 input","FC/SFC/MD bodies unchanged",
   "CLASSIC bootstrap 0x80A38000..0x80A3823F unchanged",
   "Test122 UI/input/B/suppression unchanged"]
 },indent=2)+"\n")
 print("PASS output SHA",sha(o)); print(f"PASS LCFG CRC 0x{crc:08X}")
if __name__=="__main__": main()
