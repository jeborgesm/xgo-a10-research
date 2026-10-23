#!/usr/bin/env python3
"""Fail-closed live Setup seam verifier for hardware-proven fixed-P1 firmware.

Usage: python tools/verify_handle_toggle_setup_seam.py /path/to/XGO_Handle_As_P1_Experimental.zip
No writes. Rejects any unrecognized baseline.
"""
import hashlib
import struct
import sys
import zipfile

EXPECTED_SHA = "8a8cf7a84f7771b0fc116b80521e13d3dfbd5aace73e6053fb7494eaa7d44c4a"
EXPECTED = {
    0x359E94: 0x0828E1A2, # j existing Setup handler
    0x35D53C: 0x0828E639, # j HW-positive P1 helper
    0xA38688: 0x8FA301A4, # selected row
    0xA38690: 0x8D0889C0, # Refresh pending
    0xA38694: 0x11000003, # pending conditional
    0xA3869C: 0x0828E192, # consume Refresh
    0xA386A4: 0x10600003, # stock row 0
    0xA386AC: 0x080D67A8, # stock other rows
    0xA386B4: 0x080D5D1A, # stock row 0 target
    0xA398E4: 0x14E00005, # fixed-P1 helper entry
}

def verify(data):
    digest = hashlib.sha256(data).hexdigest()
    assert digest == EXPECTED_SHA, "unexpected BIOS SHA256: " + digest
    for offset, expected in EXPECTED.items():
        got = struct.unpack_from("<I", data, offset)[0]
        assert got == expected, f"word {offset:#x}: {got:#010x} != {expected:#010x}"
    assert data[0xA38664:0xA38688] == bytes(0x24), "Setup local gap occupied"
    print("PASS: HW-positive P1 baseline and current Setup/Refresh seam verified")
    print("WARNING: local 36-byte zero gap is NOT proof of safe code allocation")
    print("WARNING: no mode state, UI toggle, or firmware candidate created")

if __name__ == "__main__":
    with zipfile.ZipFile(sys.argv[1]) as z:
        verify(z.read("bios/bisrv.asd"))
