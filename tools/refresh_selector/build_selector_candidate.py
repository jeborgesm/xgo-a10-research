#!/usr/bin/env python3
"""Fail-closed skeleton patcher for the first-class REFRESH GAMES selector.

This intentionally does NOT emit a hardware candidate yet.  It proves baseline,
cave ownership, and every currently closed patch site before instruction
construction is allowed to write anything.
"""
from pathlib import Path
import hashlib, struct, sys

BASE = 0x80000000
BASELINE_SHA = "b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e"
CAVE_START = 0x80A389B8
CAVE_END   = 0x80A391F8
CAVE_SHA = "80b67b115f8e28f3b67fddcd4cd1daac24a054603d1dd0cb13793a299a5dadfc"

# Exact Test106 words recovered from the protected baseline.
# Values are little-endian MIPS instruction words.
EXPECTED_WORDS = {
    0x80359AA4: 0x24190003,  # li t9,3 -- diagnostic User Menu upper/wrap terminal
    0x80359E60: 0x24020003,  # li v0,3 -- diagnostic User Menu lower terminal
    0x80359EA8: 0x0828E17C,  # j 0x80A385F0 -- Test85 diagnostic row dispatcher
    0x807DB67C: 0x0828E1AF,  # j 0x80A386BC -- selective Refresh dispatcher
}

def off(addr): return addr - BASE

def u32le(data, addr):
    return struct.unpack_from("<I", data, off(addr))[0]

def sha256(b): return hashlib.sha256(b).hexdigest()

def audit(path):
    data = Path(path).read_bytes()
    got = sha256(data)
    if got != BASELINE_SHA:
        raise SystemExit(f"FAIL baseline SHA {got}")
    cave = data[off(CAVE_START):off(CAVE_END)]
    if len(cave) != CAVE_END-CAVE_START or any(cave):
        raise SystemExit("FAIL reserved selector cave is not pristine")
    if sha256(cave) != CAVE_SHA:
        raise SystemExit("FAIL selector cave SHA mismatch")
    for addr, expected in EXPECTED_WORDS.items():
        actual = u32le(data, addr)
        if actual != expected:
            raise SystemExit(
                f"FAIL patch-site {addr:#010x}: got {actual:#010x}, expected {expected:#010x}"
            )
    print("PASS exact Test106 baseline")
    print(f"PASS reserved cave {CAVE_START:#010x}..{CAVE_END:#010x}")
    for addr, word in EXPECTED_WORDS.items():
        print(f"PASS site {addr:#010x} = {word:#010x}")
    print("AUDIT ONLY: no firmware bytes written")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: build_selector_candidate.py bisrv.asd")
    audit(sys.argv[1])
