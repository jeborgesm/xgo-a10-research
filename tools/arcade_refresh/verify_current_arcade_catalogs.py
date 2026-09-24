#!/usr/bin/env python3
"""Validate current four Arcade catalog triplets and simulate one append.

Point --resources at the Resources directory from a current SD snapshot.
No files are modified.
"""
from pathlib import Path
import sys
from arcade_descriptors import FAMILIES, COMMON
from catalog_codec import validate_triplet, append_record, assert_stable_prefix

EXPECTED_CURRENT_COUNTS={"cps1":27,"cps2":28,"igs":6,"neogeo":117}

def main(root: Path):
    for family in COMMON["family_order"]:
        d=FAMILIES[family]
        paths=[root/x for x in d["catalog"]]
        raw=[p.read_bytes() for p in paths]
        cs=validate_triplet(*raw)
        count=cs[0].count
        assert count==EXPECTED_CURRENT_COUNTS[family], (family,count)
        fake=f"__XGO_ARCADE_REFRESH_OFFLINE_{family.upper()}__.zfb"
        out=append_record(*raw,fake,f"XGO Offline {family.upper()}")
        assert out[3]
        for before,after in zip(raw,out[:3]):
            assert_stable_prefix(before,after)
        again=append_record(*out[:3],fake,"ignored")
        assert not again[3]
        assert again[:3]==out[:3]
        print(f"PASS {family}: {count} -> {count+1}; second append byte-identical no-op")

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: verify_current_arcade_catalogs.py <Resources-dir>")
    main(Path(sys.argv[1]))
