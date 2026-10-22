#!/usr/bin/env python3
"""Fail-closed audit of the HW-positive Handle-as-P1 firmware.

Usage: python tools/audit_handle_toggle_baseline.py XGO_Handle_As_P1_Experimental.zip
This tool NEVER modifies the supplied ZIP or firmware.
"""
import hashlib
import struct
import sys
import zipfile

EXPECTED_SHA = "8a8cf7a84f7771b0fc116b80521e13d3dfbd5aace73e6053fb7494eaa7d44c4a"
SIZE = 12768452
HOOK = 0x35D53C
HELPER = 0xA398E4
EXPECTED_HOOK = (0x0828E639, 0x00000000)
EXPECTED_HELPER = (
    0x14E00005, 0x00000000, 0x8F89F2D8, 0x0289A025,
    0x10000002, 0x00000000, 0x0000A021, 0x00D43025,
    0x30D20020, 0x080D7551, 0x00000000,
)


def crc32_mpeg2(payload):
    value = 0xFFFFFFFF
    for octet in payload:
        value ^= octet << 24
        for _ in range(8):
            value = ((value << 1) ^ (0x04C11DB7 if value & 0x80000000 else 0)) & 0xFFFFFFFF
    return value


def words(blob, start, count):
    return struct.unpack_from("<" + "I" * count, blob, start)


def audit(path):
    with zipfile.ZipFile(path) as archive:
        blob = archive.read("bios/bisrv.asd")
    assert len(blob) == SIZE, "unexpected firmware size"
    assert hashlib.sha256(blob).hexdigest() == EXPECTED_SHA, "not the HW-positive firmware"
    assert words(blob, HOOK, 2) == EXPECTED_HOOK, "hook changed"
    assert words(blob, HELPER, 11) == EXPECTED_HELPER, "helper changed"
    assert blob[HELPER + 44:HELPER + 48] == bytes(4), "helper tail changed"
    stored = words(blob, 0x18C, 1)[0]
    calculated = crc32_mpeg2(blob[0x200:])
    assert stored == calculated, "LCFG payload checksum mismatch"
    assert words(blob, 0x184, 1)[0] == SIZE - 0x200, "payload length mismatch"
    print("PASS: HW-positive image identity, hook, helper, LCFG length and CRC")
    print("SAFEGUARD: no toggle firmware was produced; input was not modified")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: audit_handle_toggle_baseline.py <firmware.zip>")
    audit(sys.argv[1])
