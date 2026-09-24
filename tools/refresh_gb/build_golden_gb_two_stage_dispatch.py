#!/usr/bin/env python3
"""Build the hardware-proven GB two-stage Refresh dispatcher.

This preserves the final Game Boy closure:
  GB/refresh.xgc -> GB/catalog.xgc -> native status/epilogue.

The caller patch fixes two independently proven defects:
1. the materializer-only exit at 0x80A3907C made the catalog block unreachable;
2. the catalog runner must explicitly initialize a0 with
   /mnt/sda1/GB/catalog.xgc before invoking the generic helper runner.

The executable GB helpers are preserved by exact SHA-256 identity rather than
embedded in this public repository.
"""
from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path

BASE=0x80000000
INPUT_SHA="9d9030b1d4218561e8c042d406cb035bf8679b15166dcdedd601299429639acb"
OUTPUT_SHA="b4b1ffa3e92c61d042b77345a21c16d67fcf586c8af6127dbc545997942f5542"
EXPECTED_CRC=0xBB3E41F0
GB_REFRESH_SHA="34f4714ecbe5affc97b7a0b87726944c253286c3baa3531e437e982174bda238"
GB_CATALOG_SHA="66030c93bfde3e790140265b1123b0ca6cb684efc251a9f602bad480ac7cbbfb"

HEADER_SIZE=0x200
SIZE_OFFSET=0x184
CRC_OFFSET=0x18C
POLY=0x04C11DB7

def sha(b): return hashlib.sha256(b).hexdigest()
def put(b,off,w): struct.pack_into("<I",b,off,w)

def crc32_mpeg2(data):
    c=0xffffffff
    for byte in data:
        c ^= byte<<24
        for _ in range(8):
            c=(((c<<1)^POLY) if c&0x80000000 else c<<1)&0xffffffff
    return c

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path,help="exact protected parent bisrv.asd")
    ap.add_argument("output",type=Path)
    a=ap.parse_args()
    src=a.input.read_bytes()
    if sha(src)!=INPUT_SHA:
        raise SystemExit("FAIL: input is not exact protected GB parent firmware")
    o=bytearray(src)

    # Complete materializer -> catalog continuation.
    words={
      0xA3907C:0x0828E421, # j 0x80A39084
      0xA39080:0x00000000,
      0xA39084:0x3C0480A4, # lui a0,0x80A4
      0xA39088:0x248490E0, # addiu a0,a0,0x90E0 -> /mnt/sda1/GB/catalog.xgc
      0xA3908C:0x24050A52, # li a1,2642
      0xA39090:0x0C28E0B8, # jal 0x80A382E0 generic helper runner
      0xA39094:0x00000000,
      0xA39098:0x24080000, # li t0,0
      0xA3909C:0x0048482A, # slt t1,v0,t0
      0xA390A0:0x1520FDE2, # bnez t1,0x80A3882C failure
      0xA390A4:0x00000000,
      0xA390A8:0x02028025, # or s0,s0,v0
      0xA390AC:0x0828E202, # j 0x80A38808 common native status/epilogue
      0xA390B0:0x00000000,
    }
    for off,w in words.items(): put(o,off,w)

    payload_size=struct.unpack_from("<I",o,SIZE_OFFSET)[0]
    if payload_size != len(o)-HEADER_SIZE:
        raise SystemExit("FAIL: LCFG payload size mismatch")
    crc=crc32_mpeg2(o[HEADER_SIZE:])
    struct.pack_into("<I",o,CRC_OFFSET,crc)
    if crc!=EXPECTED_CRC:
        raise SystemExit(f"FAIL: CRC {crc:08X} != {EXPECTED_CRC:08X}")
    if sha(o)!=OUTPUT_SHA:
        raise SystemExit("FAIL: output SHA mismatch")
    a.output.write_bytes(o)
    print("PASS firmware SHA",sha(o))
    print(f"PASS LCFG CRC 0x{crc:08X}")
    print("Required GB/refresh.xgc SHA",GB_REFRESH_SHA)
    print("Required GB/catalog.xgc SHA",GB_CATALOG_SHA)

if __name__=="__main__":
    main()
