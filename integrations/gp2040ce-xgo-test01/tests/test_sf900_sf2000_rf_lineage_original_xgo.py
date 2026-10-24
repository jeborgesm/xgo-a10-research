#!/usr/bin/env python3
"""Read-only BIN verifier: XGO original RF fields match SF900/SF2000 family.

Upstream source comparisons:
  axgdev/UniFrog: foundation/src/platform/sf2000/input/unifrog_input_wireless.c
  fernandoalves25/sf900-esp32-dongle: docs/PROTOCOL.md
This verifier does NOT establish RF hardware population on the user's XGO.
"""
import hashlib
import struct
import sys
import zipfile
from pathlib import Path

KNOWN_SHA = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
RF_FINGERPRINT = {
    "RF channels 2404/2429/2449/2479 MHz": "041d314f",
    "RX address pipe 1": "b29d594fe3",
    "RX address pipe 0": "dca8f36b74",
    "RF calibration": "f6375d",
    "baseband calibration": "0a6d679c46",
}
MIPS = {
    0x35D6E8: 0x30430040,  # andi v1,v0,0x40: RX_DR ready
    0x35DE44: 0x24040061,  # li a0,0x61: payload read
    0x35DE4C: 0x24050002,  # li a1,2: 2-byte payload
    0x35DE7C: 0x32080002,  # andi t0,s0,0x2: pipe select
}
BUTTONS = {
    "R": 0x1000, "Y": 0x2000, "X": 0x4000, "L": 0x0800,
    "A": 0x0080, "B": 0x0040, "SELECT": 0x0020, "START": 0x0010,
    "UP": 0x0008, "DOWN": 0x0004, "LEFT": 0x0002, "RIGHT": 0x0001,
}
SERIAL_ORDER = "R Y X L A B SELECT START UP DOWN LEFT RIGHT".split()

def main(filename):
    if zipfile.is_zipfile(filename):
        with zipfile.ZipFile(filename) as z:
            blob = z.read("bios/bisrv.asd")
    else:
        blob = Path(filename).read_bytes()
    assert hashlib.sha256(blob).hexdigest() == KNOWN_SHA
    for name, hex_value in RF_FINGERPRINT.items():
        value = bytes.fromhex(hex_value)
        assert blob.count(value) == 1, (name, blob.count(value))
        print(f"BIN: {name}: {hex(blob.index(value))}")
    for offset, expected in MIPS.items():
        actual = struct.unpack_from("<I", blob, offset)[0]
        assert actual == expected, (hex(offset), hex(actual), hex(expected))
    assert [BUTTONS[x] for x in SERIAL_ORDER] == [
        0x1000, 0x2000, 0x4000, 0x0800, 0x0080, 0x0040,
        0x0020, 0x0010, 0x0008, 0x0004, 0x0002, 0x0001,
    ]
    assert (0x40 & 0x02) == 0 and (0x42 & 0x02) == 0x02
    print("PASS: 5 unique RF byte sequences, 4 original MIPS opcodes, "
          "12-button bitmap, P1/P2 pipe selection")
    print("LIMIT: compatible RF firmware is not proof of installed RF hardware "
          "or actual XGO receipt of an SF900 packet")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python test_sf900_sf2000_rf_lineage_original_xgo.py XGoAnalisis.zip")
    main(sys.argv[1])
