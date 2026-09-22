#!/usr/bin/env python3
"""Build Test124 GB/GBC/GBA individual native Refresh from exact HW-proven Test123."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
BASE=0x80000000
INPUT_SHA="7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5"
EXPECTED_OUTPUT_SHA="9b007455642c4a5ac9f2cf05b5304cdcc5a6f223f8eefc043966205cbcb6ebdc"
EXPECTED_CRC=0x01D2D7DD
A=0x80A38840; END=0x80A38900
SCANNER=0x807DAE4C
UPDATED=0x807DB6C0; NO_NEW=0x807DB6EC; FAILED=0x807DB718
CLASSIC=0x80A38000; MD=0x80A387AC
POLY=0x04C11DB7
def off(a): return a-BASE
def sha(b): return hashlib.sha256(b).hexdigest()
def iop(op,rs,rt,imm): return (op<<26)|(rs<<21)|(rt<<16)|(imm&0xffff)
def jop(op,a): return (op<<26)|((a>>2)&0x03ffffff)
def crc32_mpeg2(data):
 c=0xffffffff
 for x in data:
  c^=x<<24
  for _ in range(8): c=(((c<<1)^POLY) if c&0x80000000 else c<<1)&0xffffffff
 return c
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("test123",type=Path); ap.add_argument("output",type=Path); ap.add_argument("--manifest",type=Path)
 a=ap.parse_args(); src=a.test123.read_bytes()
 if sha(src)!=INPUT_SHA: raise SystemExit("FAIL: input is not exact HW-proven Test123")
 o=bytearray(src)
 # Exact Test123 extension/free-tail/string boundary.
 if struct.unpack_from("<I",o,off(A))[0]!=iop(9,0,9,2): raise SystemExit("FAIL Test123 extension mismatch")
 if any(o[off(0x80A3888C):off(END)]): raise SystemExit("FAIL extension tail not free")
 strings=bytes(o[off(END):off(0x80A389C0)])
 bootstrap=bytes(o[off(CLASSIC):off(0x80A38240)])
 bodies=bytes(o[off(0x80A386F4):off(A)])
 ui=bytes(o[off(0x80359AFC):off(0x80359BB0)])
 items=[]; labels={}; fix=[]
 def label(n): labels[n]=A+4*len(items)
 def emit(x): items.append(x)
 def li(rt,v): emit(iop(9,0,rt,v))
 def nop(): emit(0)
 def j(x): emit(jop(2,x)); nop()
 def jal(x): emit(jop(3,x)); nop()
 def lw(rt,imm,rs): emit(iop(35,rs,rt,imm))
 def addiu(rt,rs,imm): emit(iop(9,rs,rt,imm))
 def slt(rd,rs,rt): emit((rs<<21)|(rt<<16)|(rd<<11)|0x2A)
 def beq(rs,rt,l): fix.append((len(items),4,rs,rt,l)); emit(0); nop()
 def bne(rs,rt,l): fix.append((len(items),5,rs,rt,l)); emit(0); nop()
 def unwind(): lw(31,0x1c,29); lw(16,0x18,29); addiu(29,29,0x20)
 # t0=command. 2 keeps MD, 7 keeps CLASSIC, 6 stays intentionally inert.
 li(9,2); beq(8,9,"md")
 li(9,7); beq(8,9,"classic")
 li(9,6); beq(8,9,"safe_no_new")
 emit(iop(9,8,4,0))                 # a0=t0; legal remainder is 3/4/5
 jal(SCANNER)
 slt(9,2,0); bne(9,0,"fail")        # v0 < 0
 beq(2,0,"no_new")                  # v0 == 0
 label("updated"); unwind(); j(UPDATED)
 label("no_new"); unwind(); j(NO_NEW)
 label("fail"); unwind(); j(FAILED)
 label("safe_no_new"); unwind(); j(NO_NEW)
 label("classic"); unwind(); li(21,0); j(CLASSIC)
 label("md"); j(MD)
 for idx,op,rs,rt,l in fix:
  pc=A+idx*4; imm=(labels[l]-(pc+4))//4; items[idx]=iop(op,rs,rt,imm)
 if len(items)*4>END-A: raise SystemExit("FAIL adapter overflow")
 # Replace only Test123 extension allocation.
 o[off(A):off(END)]=bytes(END-A)
 struct.pack_into("<"+"I"*len(items),o,off(A),*items)
 if bytes(o[off(END):off(0x80A389C0)])!=strings: raise SystemExit("FAIL strings changed")
 if bytes(o[off(CLASSIC):off(0x80A38240)])!=bootstrap: raise SystemExit("FAIL CLASSIC bootstrap changed")
 if bytes(o[off(0x80A386F4):off(A)])!=bodies: raise SystemExit("FAIL FC/SFC/MD bodies changed")
 if bytes(o[off(0x80359AFC):off(0x80359BB0)])!=ui: raise SystemExit("FAIL UI lifecycle changed")
 struct.pack_into("<I",o,0x184,len(o)-0x200)
 crc=crc32_mpeg2(o[0x200:]); struct.pack_into("<I",o,0x18c,crc)
 if crc!=EXPECTED_CRC or struct.unpack_from("<I",o,0x18c)[0]!=crc32_mpeg2(o[0x200:]): raise SystemExit("FAIL reseal")
 if sha(o)!=EXPECTED_OUTPUT_SHA: raise SystemExit("FAIL final SHA")
 a.output.write_bytes(o)
 m={"input_sha256":INPUT_SHA,"output_sha256":EXPECTED_OUTPUT_SHA,"lcfg_crc32_mpeg2":f"0x{crc:08X}",
    "adapter":{"address":"0x80A38840","bytes":len(items)*4,"allocation_end":"0x80A38900"},
    "commands":{"2":"existing MD","3":"native scanner list 3 GB","4":"native scanner list 4 GBC","5":"native scanner list 5 GBA","6":"native No New Games / Arcade inert","7":"Test123 CLASSIC"},
    "invariants":["exact Test123 input","FC/SFC/MD bodies unchanged","CLASSIC bootstrap unchanged","Test122/Test123 UI/input/B/re-entry/suppression unchanged","0x80A38900+ strings/data unchanged"]}
 mp=a.manifest or a.output.with_suffix(a.output.suffix+".manifest.json"); mp.write_text(json.dumps(m,indent=2)+"\n")
 print("PASS",sha(o),f"CRC=0x{crc:08X}","adapter_bytes",len(items)*4)
if __name__=="__main__": main()
