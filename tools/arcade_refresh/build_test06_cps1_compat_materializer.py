#!/usr/bin/env python3
"""Build the first CPS1 compatibility-gated materializer from HW-proven Test05A.

This does not touch bisrv.asd. It patches only the CPS1 external materializer:
- installs the audited resident Stage2 loader/hook in the proven zero cave;
- replaces the two instructions at +0x0530 with j hook / nop.
The hook replays the displaced register loads before continuing at +0x0534.
"""
import argparse,hashlib,struct
PARENT_SHA="2d6503ae20937bd9d525d68a18ee845d942667b582e71e2371450a83d8d29ad2"
HOOK_OFF=0x2600
SPLICE_OFF=0x530
HOOK_ADDR=0x87002600
MAX_HOOK_END=0x100000

def sha(b): return hashlib.sha256(b).hexdigest()
def jword(addr): return 0x08000000 | ((addr>>2)&0x03ffffff)

def main():
 ap=argparse.ArgumentParser();ap.add_argument("parent");ap.add_argument("hook");ap.add_argument("output");a=ap.parse_args()
 p=bytearray(open(a.parent,"rb").read());h=open(a.hook,"rb").read()
 if sha(p)!=PARENT_SHA: raise SystemExit("wrong Test05A parent")
 if HOOK_OFF+len(h)>MAX_HOOK_END: raise SystemExit("hook overlaps JPEG decoder")
 if any(p[HOOK_OFF:HOOK_OFF+len(h)]): raise SystemExit("hook cave is not zero")
 expected=bytes.fromhex("7c00c58fb800c68f")
 if p[SPLICE_OFF:SPLICE_OFF+8]!=expected: raise SystemExit("unexpected +0x0530 splice bytes")
 p[HOOK_OFF:HOOK_OFF+len(h)]=h
 p[SPLICE_OFF:SPLICE_OFF+8]=struct.pack("<II",jword(HOOK_ADDR),0)
 open(a.output,"wb").write(p)
 print(f"parent={PARENT_SHA}")
 print(f"hook_sha256={sha(h)} hook_bytes={len(h)}")
 print(f"output_sha256={sha(p)} bytes={len(p)}")
 print(f"splice={p[SPLICE_OFF:SPLICE_OFF+8].hex()} hook_off=0x{HOOK_OFF:x}")

if __name__=="__main__":main()
