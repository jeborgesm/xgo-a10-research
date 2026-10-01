#!/usr/bin/env python3
"""Audit the exact Test04 CPS1 compatibility-hook live state.

This proves the earliest useful hook after source pathname construction:
  +0x04B4..+0x04CC builds /mnt/sda1/ARCADE/CPS1/import/<entry>
  source pathname workspace = 0x87600100
  driver stem workspace      = 0x87600500
The hook may therefore pass a family constant plus those two pointers without
inventing firmware globals or reparsing directory state.
"""
from __future__ import annotations
import hashlib,struct,sys,pathlib
SHA="301df6494c89928cf615a918b76f81d4c0774d864cd45c77cacc2e145fed3f28"
SIZE=0x101F08
WORDS={
  0x00C8:0x36E10500, # ori at,s7,0x500
  0x00CC:0xAFC100B8, # sw at,0xb8(fp)
  0x0128:0x36E10100, # ori at,s7,0x100
  0x012C:0xAFC10094, # sw at,0x94(fp)
  0x04B4:0x8FC40094, # lw a0,0x94(fp)
  0x04B8:0x8FC500A4, # lw a1,0xa4(fp) -> %s/%s
  0x04BC:0x8FC60084, # lw a2,0x84(fp) -> family import dir
  0x04C0:0x8FD500B0, # lw s5,0xb0(fp) -> formatter
  0x04C4:0x02A0C825, # move t9,s5
  0x04C8:0x0320F809, # jalr t9
  0x04CC:0x02403825, # delay: move a3,s2 -> entry basename
}
LITERALS={
  0x0FFD:b"%s/%s\0",
  0x1200:b"/mnt/sda1/ARCADE/CPS1/import\0",
}
def u32(b,o):return struct.unpack_from("<I",b,o)[0]
def main():
 if len(sys.argv)!=2:raise SystemExit("usage: audit_test04_compat_hook.py refresh.xgc")
 b=pathlib.Path(sys.argv[1]).read_bytes()
 assert len(b)==SIZE,(len(b),SIZE)
 assert hashlib.sha256(b).hexdigest()==SHA
 for o,w in WORDS.items():assert u32(b,o)==w,(hex(o),hex(u32(b,o)),hex(w))
 for o,s in LITERALS.items():assert b[o:o+len(s)]==s,(hex(o),b[o:o+len(s)],s)
 print("PASS exact Test04 compatibility hook")
 print("hook_after=+0x04CC")
 print("source_path=0x87600100 frame+0x94")
 print("driver_stem=0x87600500 frame+0xB8")
 print("family=CPS1 constant 0")
if __name__=="__main__":main()
