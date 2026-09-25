#!/usr/bin/env python3
from family_handoff import *

def must_fail(fn):
    try: fn()
    except ValueError: return
    raise AssertionError("expected ValueError")

def main():
    m=encode_manifest(["Cadillacs and Dinosaurs.zfb","Cadillacs and Dinosaurs.zfb","Pac-Man.zfb"])
    assert m == b"Cadillacs and Dinosaurs.zfb\nPac-Man.zfb\n"
    assert decode_manifest(m)==["Cadillacs and Dinosaurs.zfb","Pac-Man.zfb"]
    assert merge_slot0(["Existing.zfb"],m)==["Existing.zfb","Cadillacs and Dinosaurs.zfb","Pac-Man.zfb"]
    assert merge_slot0(["Cadillacs and Dinosaurs.zfb"],m)==["Cadillacs and Dinosaurs.zfb","Pac-Man.zfb"]
    assert decode_manifest(b"")==[]
    for bad in ["../x.zfb","x/evil.zfb","x.zip",".zfb","x.zfb\nother.zfb"]:
        must_fail(lambda bad=bad: validate_zfb_name(bad))
    must_fail(lambda: decode_manifest(b"x.zfb"))
    must_fail(lambda: decode_manifest(b"x.zfb\x00\n"))
    print("PASS family handoff contract")

if __name__=="__main__": main()
