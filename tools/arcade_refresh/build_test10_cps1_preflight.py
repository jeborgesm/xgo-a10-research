#!/usr/bin/env python3
import argparse,hashlib,struct
PARENT_SHA="2d6503ae20937bd9d525d68a18ee845d942667b582e71e2371450a83d8d29ad2"
HOOK_OFF=0x2600
ENTRY_CALL_OFF=0x8
HOOK_ADDR=0x87002600
EXPECTED=bytes.fromhex("0800c00d")
def sha(b): return hashlib.sha256(b).hexdigest()
def jal(a): return struct.pack("<I",0x0c000000|((a>>2)&0x03ffffff))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("parent");ap.add_argument("hook");ap.add_argument("output");a=ap.parse_args()
 b=bytearray(open(a.parent,"rb").read());h=open(a.hook,"rb").read()
 if sha(b)!=PARENT_SHA: raise SystemExit("wrong Test05A parent")
 if b[ENTRY_CALL_OFF:ENTRY_CALL_OFF+4]!=EXPECTED: raise SystemExit("unexpected Test05A entry call")
 if any(b[HOOK_OFF:HOOK_OFF+len(h)]): raise SystemExit("preflight cave not zero")
 b[HOOK_OFF:HOOK_OFF+len(h)]=h
 b[ENTRY_CALL_OFF:ENTRY_CALL_OFF+4]=jal(HOOK_ADDR)
 open(a.output,"wb").write(b)
 print("parent",PARENT_SHA);print("hook",sha(h),len(h));print("output",sha(b),len(b));print("entry",b[:16].hex())
if __name__=="__main__": main()
