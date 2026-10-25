#!/usr/bin/env python3
"""BIN: verify that P1 physical R level changes P2 first-bit sample path.
Uses original user archive; not a time/voltage measurement or hardware test.
"""
import hashlib
import struct
import sys
import zipfile
from pathlib import Path

ORIGINAL = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
WORDS = {
    0x35d844: 0xae2e0000,  # built-in B15 output drive release
    0x35d864: 0xae0b0000,  # external L0 output drive release
    0x35d868: 0x0c0b81de,  # helper after external drive release
    0x35d870: 0x8e8a0000,  # read built-in physical B15
    0x35d874: 0x31498000,  # test bit15 / physical R
    0x35d878: 0x15200005,  # bne P1bit,zero, +5 to P2 sample
    0x35d87c: 0x36710050,  # MIPS delay slot on both paths
    0x35d880: 0x8f91f2d4,  # four additional instructions only on P1 LOW
    0x35d884: 0x36301000,
    0x35d888: 0xaf90f2d4,
    0x35d88c: 0x36710050,
    0x35d890: 0x8e390000,  # sample external physical L0 / R0
    0x35d894: 0x33330001,  # extract L0 slot0
}

def verify(file):
    if zipfile.is_zipfile(file):
        with zipfile.ZipFile(file) as archive:
            b=archive.read("bios/bisrv.asd")
    else:
        b=Path(file).read_bytes()
    assert hashlib.sha256(b).hexdigest()==ORIGINAL
    for off, expected in WORDS.items():
        actual=struct.unpack_from("<I",b,off)[0]
        assert actual==expected,(hex(off),hex(actual),hex(expected))
    branch=WORDS[0x35d878]
    assert (branch>>26)==5  # MIPS bne
    signed_disp=struct.unpack("<h",struct.pack("<H",branch&0xffff))[0]
    assert 0x35d878+4+(signed_disp<<2)==0x35d890
    for p1_r_released in (True,False):
        bit=0x8000 if p1_r_released else 0
        taken=bool(bit&0x8000)
        path=[0x35d87c]+([] if taken else
                          [0x35d880,0x35d884,0x35d888,0x35d88c])
        print(f"P1 R {'RELEASED HIGH' if taken else 'PRESSED LOW'}: "
              f"{len(path)} instructions from conditional branch before "
              "L0/P2 first-bit read (includes common MIPS delay slot)")
        assert len(path)==(1 if taken else 5)
    print("PASS BIN: native R press executes 4 additional instructions before "
          "external R sample; default released native R samples sooner")
    print("LIMIT: not measured microseconds, actual data rise, or physical fault")

if __name__=="__main__":
    if len(sys.argv)!=2:
        sys.exit("usage: python verify_xgo_p1_r_conditioned_p2_first_sample.py XGoAnalisis.zip")
    verify(sys.argv[1])
