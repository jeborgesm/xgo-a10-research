#!/usr/bin/env python3
"""Read-only original XGO BIN verifier: full 12-clock host scan.

Usage: python verify_original_xgo_12_clock_train.py XGoAnalisis.zip
Original XGO firmware SHA is pinned; never patch firmware here.
"""

import hashlib
import struct
import sys
import zipfile
from pathlib import Path

SHA="869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
CALL_DELAY=0x0c0c3fb4 # jal 0x8030fed0
TWO_US=0x24040002
FOUR_US=0x24040004
FALL_DELAYS=(0x35D8C8,0x35D940,0x35D9B8,0x35DA30,
             0x35DAA8,0x35DB20,0x35DB98,0x35DC10,
             0x35DC84,0x35DCF8,0x35DD6C,0x35DDE0)
CLOCK_LOW_STORES=(0x35D8BC,0x35D934,0x35D9AC,0x35DA24,
                  0x35DA9C,0x35DB14,0x35DB8C,0x35DC04,
                  0x35DC78,0x35DCEC,0x35DD60,0x35DDD4)
CLOCK_HIGH_STORES=(0x35D8E4,0x35D95C,0x35D9D4,0x35DA4C,
                   0x35DAC4,0x35DB3C,0x35DBB4,0x35DC2C,
                   0x35DCA0,0x35DD14,0x35DD88,0x35DDFC)

def verify(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            firmware=archive.read("bios/bisrv.asd")
    else:
        firmware=Path(path).read_bytes()
    assert hashlib.sha256(firmware).hexdigest()==SHA
    opcode=lambda at:struct.unpack_from("<I",firmware,at)[0]
    delay_calls=[at for at in range(0x35D770,0x35DE10,4)
                 if opcode(at)==CALL_DELAY]
    assert delay_calls==[0x35D824,*FALL_DELAYS]
    assert opcode(0x35D828)==FOUR_US
    assert all(opcode(at+4)==TWO_US for at in FALL_DELAYS)
    for fall,delay,rise in zip(CLOCK_LOW_STORES,FALL_DELAYS,CLOCK_HIGH_STORES):
        assert fall<delay<rise
        for at in (fall,rise):
            word=opcode(at)
            assert word>>26==43 and ((word>>21)&31)==18 and word&0xffff==0
    assert opcode(0x35D870)==0x8e8a0000
    assert opcode(0x35D890)==0x8e390000
    print("PASS: original MIPS scanner reads both channel slot0 bits BEFORE CLOCK")
    print("PASS: exactly 12 intended B7 LOW/HIGH clock phases, each nominal 2us LOW")
    print("PASS: one preceding host LOAD delay of nominal 4us")
    print("LIMIT: source instruction chronology is NOT a live voltage/edge waveform")

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: python verify_original_xgo_12_clock_train.py XGoAnalisis.zip")
    verify(sys.argv[1])
