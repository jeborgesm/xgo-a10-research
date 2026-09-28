#!/usr/bin/env python3
import argparse,hashlib,struct
PARENT="301df6494c89928cf615a918b76f81d4c0774d864cd45c77cacc2e145fed3f28"
HOOK_OFF=0x2600
HOOK_ADDR=0x87002600
CALL_OFF=0x052c
EXPECTED_CALL=bytes.fromhex("a000d28f7c00c58f")
OLD_JPG=b"/mnt/sda1/ARCADE/CPS1/art/.xgo.jpg\0"
NEW_JPG=b"/mnt/sda1/ARCADE/.xgo.jpg\0"
OLD_RGB=b"/mnt/sda1/ARCADE/CPS1/art/.xgo.rgb565\0"
NEW_RGB=b"/mnt/sda1/ARCADE/.xgo.rgb565\0"

def jal(addr): return struct.pack("<I",0x0c000000|((addr>>2)&0x03ffffff))
def patch_literal(b,old,new):
 p=b.find(old)
 if p<0: raise SystemExit("required Test04 artwork literal not found")
 b[p:p+len(old)]=new+b"\0"*(len(old)-len(new))
 return p

def main():
 ap=argparse.ArgumentParser();ap.add_argument("parent");ap.add_argument("hook");ap.add_argument("output");a=ap.parse_args()
 b=bytearray(open(a.parent,"rb").read());h=open(a.hook,"rb").read()
 if hashlib.sha256(b).hexdigest()!=PARENT: raise SystemExit("wrong Test04 parent")
 if len(h)>0x100000-HOOK_OFF: raise SystemExit("hook overlaps JPEG decoder")
 if any(b[HOOK_OFF:HOOK_OFF+len(h)]): raise SystemExit("hook target is not zero-filled")
 if b[CALL_OFF:CALL_OFF+8]!=EXPECTED_CALL: raise SystemExit("unexpected +0x052c hook boundary")
 jp=patch_literal(b,OLD_JPG,NEW_JPG);rp=patch_literal(b,OLD_RGB,NEW_RGB)
 b[HOOK_OFF:HOOK_OFF+len(h)]=h
 b[CALL_OFF:CALL_OFF+8]=jal(HOOK_ADDR)+b"\0\0\0\0"
 open(a.output,"wb").write(b)
 print("parent",PARENT)
 print("hook_sha256",hashlib.sha256(h).hexdigest(),"bytes",len(h))
 print("artwork_offsets",hex(jp),hex(rp))
 print("hook_call",b[CALL_OFF:CALL_OFF+8].hex())
 print("output_sha256",hashlib.sha256(b).hexdigest(),"bytes",len(b))
if __name__=="__main__":main()
