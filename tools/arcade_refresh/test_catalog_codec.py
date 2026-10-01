#!/usr/bin/env python3
"""Offline invariants for Arcade catalog codec.

Can run without SD/card data. Current captured triplets should additionally be
fed through verify_current_arcade_catalogs.py when available locally.
"""
import struct
from catalog_codec import parse_catalog, append_record, assert_stable_prefix

def make(values):
    raw=[x.encode("utf-8") for x in values]
    blob=b"".join(x+b"\0" for x in raw)
    offs=[]; p=0
    for x in raw:
        offs.append(p); p += len(x)+1
    return struct.pack("<I",len(raw)) + (struct.pack(f"<{len(raw)}I",*offs) if raw else b"") + blob

s0=make(["A.zfb","B.zfb"])
s1=make(["甲","Beta"])
s2=make(["J","BETA"])
o0,o1,o2,changed=append_record(s0,s1,s2,"New Game.zfb","New Game")
assert changed
for a,b in zip((s0,s1,s2),(o0,o1,o2)):
    assert_stable_prefix(a,b)
assert parse_catalog(o0).strings[-1]==b"New Game.zfb"
assert parse_catalog(o1).strings[-1]==b"New Game"
assert parse_catalog(o2).strings[-1]==b"New Game"

# Idempotence is exact slot0 identity and must leave every byte unchanged.
r0,r1,r2,changed=append_record(o0,o1,o2,"New Game.zfb","Different metadata ignored")
assert not changed
assert (r0,r1,r2)==(o0,o1,o2)

# Count mismatch must fail closed.
try:
    append_record(s0,make(["one"]),s2,"X.zfb","X")
except ValueError:
    pass
else:
    raise AssertionError("misaligned triplet accepted")

# Footer/padding must fail closed rather than being destroyed.
try:
    parse_catalog(s0+b"X")
except ValueError:
    pass
else:
    raise AssertionError("catalog footer accepted")

print("PASS catalog stable append, byte preservation, idempotence, fail-closed checks")
