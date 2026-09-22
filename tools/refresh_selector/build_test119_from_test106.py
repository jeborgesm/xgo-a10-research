#!/usr/bin/env python3
"""Deterministically build Test119 from exact Test106.

No prior test ZIP is an input. The HW-proven Test118 selector/renderer image is
preserved below as a compressed, SHA-checked source fixture; the Test119 logic
is emitted from MIPS instruction constructors.

Test119 delta:
  active A row 0..7 -> save command, clear active, normalize caller User Menu
  selection to row 3, then enter native Refresh.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,struct,zlib
from pathlib import Path
BASE=0x80000000
BASELINE_SHA="b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e"
EXPECTED_TEST118_SHA="24c89ea7b39edf923d96a5cfa1e2a77cdda2245ae6d1e021ca4699acbc832d2f"
EXPECTED_TEST119_SHA="d357a86a79175d7c07877026ccfaa94c352fd571ba7d54b08d1e9acf1cdf4c15"
EXPECTED_TEST119_CRC=0x39A338DE
HEADER_SIZE=0x200; SIZE_OFFSET=0x184; CRC_OFFSET=0x18C; POLY=0x04C11DB7
MODULE_ADDR=0x80A389C8
MODULE_ZB64="eNq1lM9r02AYx5+kdsu0hYl1dCiYwltWQaQHhR6CtG7txtigrDsU8WDo6la6ttKxobcgOzhQH0EcMm9r569tPg5UtsOcf4ZXz7uMHWQMoT5pV6khEXIwEPI84fM83zeHfOqGon1b6nnigX4hg3oW+Ormui7t0Ppdv2L29T+M3MHIYsXwah542OxfTbfYC8XOGdgMHC4/9x0u1+K3rLtae+gkY/VHpPk0GrsDvbBKAahREOp0EdZIhdck4A1F4C1dgXcUhfd0DdYpBhukwSbF4QMNAdEIbNMY7FAa9mgSvlIWPtJt2KJ25lWplXmw/wwlULRQXJEDxz0v2nX6WAnPSKdFKAtSVPYJgMKaDMVwo/E4/KthnDdnwatwPxr+2Yg3eyFv4cH+In4Cr0hBlwjFAHrhM00uPcIAn7dmnNGOnhavB/m8l0f9vtCBOaUIP0T6WmdZxDTP3neYVfDvWZMv/4P3WXjJJuulyywnPmDhZZusbZdZTryw8B6brO8us5z4qIU/ZZN15DLLidcsvNcmKyi5y3Lixyx8l01WzGWWE3/HwnfbZGVdZjnxMxae/3nkfx/ZAZyzh+wEZDcgOwLZFcjOQHYHskOQXYLsFGS3IDsG2TXIzkF2D++vIbsIDdgdmC9favppIpmaSGZG1OHEeDLD/Q2+U3qpkKuUIDN/L19V2x3AeH5aV4eqhYU8wLBeyqs3Kw/MHe1aHazMVqodfWJqQS/n8iaTqOb0Ka4GZ/W5uULuv35Ty8tBdmQ/spfPmf3KiY8l6BMb0hcyPR7L+hXT5eb73yZly1s="
MODULE_SHA="66bf98d01c3898218a03944c981c6a2d74bf7a27fbbec32c50f949bf6ebba911"
R={'zero':0,'v1':3,'t0':8,'sp':29}
def iop(op,rs,rt,imm): return (op<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def jop(op,a): return (op<<26)|((a>>2)&0x03ffffff)
def lui(rt,x): return iop(15,'zero',rt,x)
def sw(rt,x,rs): return iop(43,rs,rt,x)
def addiu(rt,rs,x): return iop(9,rs,rt,x)
def j(a): return jop(2,a)
def off(a): return a-BASE
def sha(b): return hashlib.sha256(b).hexdigest()
def crc32_mpeg2(data):
 c=0xffffffff
 for byte in data:
  c^=byte<<24
  for _ in range(8): c=(((c<<1)^POLY) if c&0x80000000 else c<<1)&0xffffffff
 return c
def patch(buf,a,data,m,label):
 old=bytes(buf[off(a):off(a)+len(data)])
 buf[off(a):off(a)+len(data)]=data
 m.append({"label":label,"address":f"0x{a:08X}","size":len(data),
           "before_sha256":sha(old),"after_sha256":sha(data)})
def reseal(buf):
 struct.pack_into("<I",buf,SIZE_OFFSET,len(buf)-HEADER_SIZE)
 c=crc32_mpeg2(bytes(buf[HEADER_SIZE:]))
 struct.pack_into("<I",buf,CRC_OFFSET,c); return c
def reconstruct_test118(base):
 if sha(base)!=BASELINE_SHA: raise SystemExit("FAIL input is not exact Test106")
 o=bytearray(base);m=[]
 patch(o,0x80356C68,bytes.fromhex("f4e3280800000000"),m,"HW-proven selector-aware B hook")
 patch(o,0x80359AA4,bytes.fromhex("72e2280800000000"),m,"HW-proven active upper terminal")
 patch(o,0x80359BA8,bytes.fromhex("96e2280800000000"),m,"HW-proven selector renderer hook")
 patch(o,0x80359E60,bytes.fromhex("7be2280800000000"),m,"HW-proven active lower terminal")
 patch(o,0x807DBB40,bytes.fromhex("202020202020202020202020200000002020202020202020202020202020202020202020202020202020202020000000"),m,"blank obsolete diagnostic labels")
 mod=zlib.decompress(base64.b64decode(MODULE_ZB64))
 if sha(mod)!=MODULE_SHA: raise SystemExit("FAIL embedded module SHA")
 patch(o,MODULE_ADDR,mod,m,"HW-proven Test118 selector/renderer/B module")
 reseal(o)
 if sha(o)!=EXPECTED_TEST118_SHA: raise SystemExit("FAIL Test118 reconstruction")
 return o,m
def main():
 ap=argparse.ArgumentParser();ap.add_argument("test106",type=Path);ap.add_argument("output",type=Path);ap.add_argument("--manifest",type=Path)
 a=ap.parse_args();t118,m=reconstruct_test118(a.test106.read_bytes());o=bytearray(t118)
 words=[lui('t0',0x80A4),sw('v1',0x89C4,'t0'),sw('zero',0x89C0,'t0'),
        addiu('t0','zero',3),sw('t0',0x1A4,'sp'),j(0x807DB5CC),0]
 data=b''.join(struct.pack("<I",w) for w in words)+bytes(0x40-4*len(words))
 patch(o,0x80A38648,data,m,"unified active A row0..7 dispatcher")
 crc=reseal(o)
 if bytes(o[off(0x80A38F70):off(0x80A38FCC)])!=bytes(t118[off(0x80A38F70):off(0x80A38FCC)]): raise SystemExit("FAIL renderer epilogue changed")
 if crc!=EXPECTED_TEST119_CRC or sha(o)!=EXPECTED_TEST119_SHA: raise SystemExit(f"FAIL final CRC/SHA {crc:#x} {sha(o)}")
 a.output.write_bytes(o);mp=a.manifest or a.output.with_suffix(a.output.suffix+".manifest.json")
 mp.write_text(json.dumps({"input_sha256":BASELINE_SHA,"output_sha256":EXPECTED_TEST119_SHA,
 "lcfg_crc32_mpeg2":f"0x{crc:08X}","changes":m,
 "invariants":["exact Test118 reconstructed from Test106","Test118 B behavior retained",
 "renderer epilogue byte-identical","A row3 is Game Boy command, not Back",
 "caller state-14 selection normalized to 3 before native Refresh"]},indent=2)+"\n")
 print(f"PASS output SHA {sha(o)}");print(f"PASS LCFG CRC 0x{crc:08X}");print(f"wrote {a.output}");print(f"wrote {mp}")
if __name__=="__main__": main()
