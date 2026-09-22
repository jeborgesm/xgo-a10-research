#!/usr/bin/env python3
"""Build Test122 from exact HW-proven Test119.

Purpose: suppress only the native state-14 172x172 Setup selector compositor
while selector_active != 0. Test119 overlay/input/Refresh lifecycle is untouched.
"""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path

BASE=0x80000000
INPUT_SHA="d357a86a79175d7c07877026ccfaa94c352fd571ba7d54b08d1e9acf1cdf4c15"
HEADER_SIZE=0x200; SIZE_OFFSET=0x184; CRC_OFFSET=0x18C; POLY=0x04C11DB7
HOOK=0x80359B3C
CONT=0x80359B68
HELPER=0x80A39000
SELECTOR_ACTIVE=0x80A389C0
SELECTOR_CALL=0x80353250
EXPECTED_BLOCK=[
  0x02802021,0x00002821,0x00003021,0x240700AC,0xAFA70014,
  0xAFAA0018,0xAFBF001C,0xAFB00020,0xAFA80024,0x0C0D4C94,0xAFA70010
]
R={'zero':0,'a0':4}
def iop(op,rs,rt,imm): return (op<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def jop(op,a): return (op<<26)|((a>>2)&0x03ffffff)
def lui(rt,x): return iop(15,'zero',rt,x)
def lw(rt,x,rs): return iop(35,rs,rt,x)
def bne(rs,rt,off): return iop(5,rs,rt,off)
def j(a): return jop(2,a)
def off(a): return a-BASE
def sha(b): return hashlib.sha256(b).hexdigest()
def crc32_mpeg2(data):
 c=0xffffffff
 for byte in data:
  c^=byte<<24
  for _ in range(8): c=(((c<<1)^POLY) if c&0x80000000 else c<<1)&0xffffffff
 return c
def words(buf,a,n): return list(struct.unpack_from('<'+'I'*n,buf,off(a)))
def put_words(buf,a,ws): struct.pack_into('<'+'I'*len(ws),buf,off(a),*ws)
def reseal(buf):
 struct.pack_into('<I',buf,SIZE_OFFSET,len(buf)-HEADER_SIZE)
 c=crc32_mpeg2(bytes(buf[HEADER_SIZE:]))
 struct.pack_into('<I',buf,CRC_OFFSET,c)
 return c

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('test119',type=Path); ap.add_argument('output',type=Path); ap.add_argument('--manifest',type=Path)
 a=ap.parse_args(); src=a.test119.read_bytes()
 if sha(src)!=INPUT_SHA: raise SystemExit('FAIL input is not exact HW-proven Test119')
 o=bytearray(src)
 if words(o,HOOK,len(EXPECTED_BLOCK))!=EXPECTED_BLOCK: raise SystemExit('FAIL native selector block mismatch')
 if any(o[off(HELPER):off(HELPER)+0x80]): raise SystemExit('FAIL helper cave is not zero/free')
 # Hook only the first two words; helper replays the complete original block when inactive.
 put_words(o,HOOK,[j(HELPER),0])

 # a0 is safe scratch here: inactive path immediately restores stock a0=s4;
 # active path skips a call that is ABI-permitted to clobber a0 anyway.
 helper=[
   lui('a0',0x80A4),
   lw('a0',0x89C0,'a0'),
   bne('a0','zero',14), # -> active jump after replay + continuation jump
   0,
   *EXPECTED_BLOCK,
   j(CONT),0,
   j(CONT),0,
 ]
 put_words(o,HELPER,helper)

 # Fail closed on protected Test119 surfaces.
 if o[off(0x80359AFC):off(0x80359B10)] != src[off(0x80359AFC):off(0x80359B10)]: raise SystemExit('FAIL repaint path changed')
 if o[off(0x80359B68):off(0x80359BB0)] != src[off(0x80359B68):off(0x80359BB0)]: raise SystemExit('FAIL post-selector/Test119 hook changed')
 if o[off(0x80A38648):off(0x80A39000)] != src[off(0x80A38648):off(0x80A39000)]: raise SystemExit('FAIL Test119 module/lifecycle changed')

 crc=reseal(o)
 # Independent reseal verification.
 stored_size=struct.unpack_from('<I',o,SIZE_OFFSET)[0]
 stored_crc=struct.unpack_from('<I',o,CRC_OFFSET)[0]
 calc=crc32_mpeg2(bytes(o[HEADER_SIZE:]))
 if stored_size!=len(o)-HEADER_SIZE or stored_crc!=calc or crc!=calc: raise SystemExit('FAIL LCFG reseal verification')

 a.output.write_bytes(o)
 manifest={
  'input_sha256':INPUT_SHA,'output_sha256':sha(o),'lcfg_crc32_mpeg2':f'0x{crc:08X}',
  'changes':[
   {'address':'0x80359B3C','size':8,'purpose':'selector-active suppression hook; replaces first two native setup words only'},
   {'address':'0x80A39000','size':len(helper)*4,'purpose':'conditional helper; inactive replays exact native 172x172 compositor block; active bypasses it'},
   {'address':'0x00000184/0x0000018C','purpose':'LCFG size/CRC reseal'}
  ],
  'invariants':[
   'exact HW-proven Test119 input','0x80359AFC..0x80359B0F repaint path unchanged',
   '0x80359B68..0x80359BAF post-selector and Test119 renderer hook unchanged',
   '0x80A38648..0x80A38FFF Test119 selector/input/Refresh lifecycle unchanged',
   'no framebuffer fill/geometry/text/footer changes'
  ]
 }
 mp=a.manifest or a.output.with_suffix(a.output.suffix+'.manifest.json'); mp.write_text(json.dumps(manifest,indent=2)+'\n')
 print('PASS output SHA',sha(o)); print(f'PASS LCFG CRC 0x{crc:08X}'); print('helper bytes',len(helper)*4)

if __name__=='__main__': main()
