#!/usr/bin/env python3
"""Build Test128: Test127 with GB catalog call bypassed.

Purpose: isolate GB materializer/runner using the historical post-Test82 method.
"""
import argparse,hashlib,struct,zipfile
from pathlib import Path
BASE=0x80000000; HDR=0x200; POLY=0x04C11DB7
IN_FW="490939aaacd210d78b667057a604414e840fdb5981d6cf5ba1305612131a917f"
GB_REFRESH="00addd59c2b3305e936021bb6cb7c66e03cac334816cd2a61e5c216315e19810"
def sha(b):return hashlib.sha256(b).hexdigest()
def off(a):return a-BASE
def jop(a):return (2<<26)|((a>>2)&0x3ffffff)
def crc(d):
 c=0xffffffff
 for x in d:
  c^=x<<24
  for _ in range(8):c=(((c<<1)^POLY) if c&0x80000000 else c<<1)&0xffffffff
 return c
def main():
 ap=argparse.ArgumentParser();ap.add_argument("test127_fw",type=Path);ap.add_argument("gb_refresh",type=Path);ap.add_argument("out",type=Path);a=ap.parse_args()
 fw=bytearray(a.test127_fw.read_bytes()); h=a.gb_refresh.read_bytes()
 assert sha(fw)==IN_FW and sha(h)==GB_REFRESH
 # Test127 GB body: after first helper success/OR, second helper starts at 0x80A3907C.
 # Replace that point with jump to common successful status tail 0x80A38808.
 p=off(0x80A3907C)
 old=struct.unpack_from("<I",fw,p)[0]
 assert old==0x3c0480a3,hex(old) # lui a0,path2 high
 struct.pack_into("<I",fw,p,jop(0x80A38808));struct.pack_into("<I",fw,p+4,0)
 struct.pack_into("<I",fw,0x184,len(fw)-HDR);c=crc(fw[HDR:]);struct.pack_into("<I",fw,0x18c,c)
 with zipfile.ZipFile(a.out,"w",zipfile.ZIP_DEFLATED) as z:
  z.writestr("bios/bisrv.asd",fw);z.writestr("GB/refresh.xgc",h)
 print("firmware",sha(fw));print("crc",f"0x{c:08X}");print("zip",sha(a.out.read_bytes()) if a.out.exists() else "written")
if __name__=="__main__":main()
