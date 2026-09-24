#!/usr/bin/env python3
"""Build Test127 GB enrichment from exact HW-proven ancestors.

Inputs:
  Test123 bios/bisrv.asd
  exact Test97 MD/refresh.xgc (also carried unchanged through Test106)
  exact Test75 FC/catalog.xgc

Produces a minimal hardware candidate containing:
  bios/bisrv.asd
  GB/refresh.xgc
  GB/catalog.xgc
"""
from pathlib import Path
import argparse, hashlib, struct, zipfile

BASE=0x80000000; HDR=0x200; POLY=0x04C11DB7
FW_IN="7becafa3372e7b511bd8f05d0f378ca6397d72c6cc5c075f2e0d650cba2a86b5"
MD_REFRESH="c0af2dea8291f86b411e819356e7b6b877ca69e39a444f0780348906f610e087"
FC_CATALOG="b12541d5daede8c6e35c0f6f3a53c35c705a7d7ea7bbb508a6ae7e1b8d956067"
GB_REFRESH="00addd59c2b3305e936021bb6cb7c66e03cac334816cd2a61e5c216315e19810"
GB_CATALOG="66030c93bfde3e790140265b1123b0ca6cb684efc251a9f602bad480ac7cbbfb"
FW_OUT="490939aaacd210d78b667057a604414e840fdb5981d6cf5ba1305612131a917f"
CRC_OUT=0x1E8CE898

def sha(b): return hashlib.sha256(b).hexdigest()
def off(a): return a-BASE
def jop(a): return (2<<26)|((a>>2)&0x3ffffff)
def jal(a): return (3<<26)|((a>>2)&0x3ffffff)
def iop(op,rs,rt,imm): return (op<<26)|(rs<<21)|(rt<<16)|(imm&0xffff)
def br(op,rs,rt,pc,target):
 d=(target-(pc+4))//4
 assert -32768<=d<=32767 and pc+4+d*4==target
 return iop(op,rs,rt,d)
def crc(data):
 c=0xffffffff
 for byte in data:
  c^=byte<<24
  for _ in range(8): c=(((c<<1)^POLY) if c&0x80000000 else c<<1)&0xffffffff
 return c

def patch_exact(b,off_,old,new):
 assert len(old)==len(new) and bytes(b[off_:off_+len(old)])==old
 b[off_:off_+len(new)]=new

def make_gb_refresh(src):
 assert len(src)==1056520 and sha(src)==MD_REFRESH
 b=bytearray(src)
 for o,a,z in [
  (0x114,bytes.fromhex("6d64"),bytes.fromhex("6762")),
  (0x2a8,b"m",b"g"),(0x2d4,b"d",b"b"),
  (0xff2,b"MD",b"GB"),(0x100d,b"MD",b"GB"),(0x101b,b"MD",b"GB"),
  (0x1036,b"MD",b"GB"),(0x1054,b"MD",b"GB"),(0x1071,b"MD",b"GB"),(0x108a,b"MD",b"GB")]:
  patch_exact(b,o,a,z)
 assert bytes(b[0x27c:0x280])==b"\0\0\0\0"
 assert sha(b)==GB_REFRESH
 return bytes(b)

def make_gb_catalog(src):
 assert len(src)==2642 and sha(src)==FC_CATALOG
 b=bytearray(src)
 for o,a,z in [
  (0x444,b"f",b"g"),(0x470,b"c",b"b"),(0x734,b"L",b"d"),
  (0x9f8,b"rdbui",b"vdsdc"),(0xa16,b"fhcfg",b"umboa"),(0xa34,b"nethn",b"qdvd6"),
  (0xa3e,b"/mnt/sda1/FC\0\0",b"/mnt/sda1/GB\0\0")]:
  patch_exact(b,o,a,z)
 assert sha(b)==GB_CATALOG
 return bytes(b)

def make_fw(src):
 assert sha(src)==FW_IN
 b=bytearray(src)
 def word(a): return struct.unpack_from("<I",b,off(a))[0]
 def put(a,w): struct.pack_into("<I",b,off(a),w)
 assert word(0x80A386EC)==jop(0x80A38840)
 assert word(0x80A38884)==jop(0x80A387AC)
 assert all(x==0 for x in b[off(0x80A39048):off(0x80A391F8)])

 P1=0x80A390C0; P2=0x80A390E0; GB=0x80A39050
 for a,s in [(P1,b"/mnt/sda1/GB/refresh.xgc\0"),(P2,b"/mnt/sda1/GB/catalog.xgc\0")]:
  assert len(s)<=0x20; b[off(a):off(a)+len(s)]=s

 RUN=0x80A382E0; FAIL=0x80A3882C; DONE=0x80A38808
 w=[]
 def emit(x): w.append(x)
 def pc(): return GB+4*len(w)
 a=P1
 emit(iop(15,0,4,(a+0x8000)>>16)); emit(iop(9,4,4,a&0xffff))
 emit(iop(15,0,5,0x10)); emit(iop(13,5,5,0x1f08)); emit(jal(RUN)); emit(0)
 emit(iop(9,0,8,0)); emit((2<<21)|(8<<16)|(9<<11)|42)
 emit(br(5,9,0,pc(),FAIL)); emit(0); emit((16<<21)|(2<<16)|(16<<11)|37)
 a=P2
 emit(iop(15,0,4,a>>16)); emit(iop(9,4,4,a&0xffff))
 emit(iop(9,0,5,2642)); emit(jal(RUN)); emit(0)
 emit(iop(9,0,8,0)); emit((2<<21)|(8<<16)|(9<<11)|42)
 emit(br(5,9,0,pc(),FAIL)); emit(0); emit((16<<21)|(2<<16)|(16<<11)|37)
 emit(jop(DONE)); emit(0)
 assert len(w)==23
 for i,x in enumerate(w): put(GB+4*i,x)

 EXT=0x80A38840; MD=0x80A387AC; CLASSIC=0x80A38000; NONEW=0x807DB6EC
 x=[]
 def ep(v): x.append(v)
 def epc(): return EXT+4*len(x)
 ep(iop(9,0,9,2)); ep(br(4,8,9,epc(),0x80A38890)); ep(0)
 ep(iop(9,0,9,3)); ep(br(4,8,9,epc(),0x80A38898)); ep(0)
 ep(iop(9,0,9,7)); ep(br(5,8,9,epc(),0x80A3887C)); ep(0)
 ep(iop(35,29,31,0x1c)); ep(iop(35,29,16,0x18)); ep(iop(9,29,29,0x20))
 ep(iop(9,0,21,0)); ep(jop(CLASSIC)); ep(0)
 assert EXT+4*len(x)==0x80A3887C
 ep(iop(35,29,31,0x1c)); ep(iop(35,29,16,0x18)); ep(iop(9,29,29,0x20)); ep(jop(NONEW)); ep(0)
 while EXT+4*len(x)<0x80A38890: ep(0)
 ep(jop(MD)); ep(0); ep(jop(GB)); ep(0)
 for a in range(EXT,0x80A388A0,4): put(a,0)
 for i,v in enumerate(x): put(EXT+4*i,v)

 struct.pack_into("<I",b,0x184,len(b)-HDR)
 c=crc(b[HDR:]); struct.pack_into("<I",b,0x18c,c)
 assert c==CRC_OUT and crc(b[HDR:])==c and sha(b)==FW_OUT
 return bytes(b)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("test123_fw",type=Path); ap.add_argument("test97_md_refresh",type=Path)
 ap.add_argument("test75_fc_catalog",type=Path); ap.add_argument("output_zip",type=Path)
 a=ap.parse_args()
 files={"bios/bisrv.asd":make_fw(a.test123_fw.read_bytes()),
        "GB/refresh.xgc":make_gb_refresh(a.test97_md_refresh.read_bytes()),
        "GB/catalog.xgc":make_gb_catalog(a.test75_fc_catalog.read_bytes())}
 with zipfile.ZipFile(a.output_zip,"w",zipfile.ZIP_DEFLATED) as z:
  for name,data in files.items(): z.writestr(name,data)
 print("PASS firmware",FW_OUT); print(f"PASS LCFG CRC 0x{CRC_OUT:08X}")
 print("PASS GB refresh",GB_REFRESH); print("PASS GB catalog",GB_CATALOG)
if __name__=="__main__": main()
