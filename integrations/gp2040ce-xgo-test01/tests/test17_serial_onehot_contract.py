#!/usr/bin/env python3
"""Offline contract: verify source mapping order and model exact 12-bit serialization.
Does NOT prove GP2040 physical pin assignments or hardware timing.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "candidates/test16-offline/XGODriver.cpp"
NAMES = ["R1","B4","B3","L1","B1","B2","S1","S2","Up","Down","Left","Right"]
EXPECTED = {name: index for index, name in enumerate(NAMES)}

def source_mapping():
    source = SRC.read_text()
    mapping = re.findall(r"g->pressed(\w+)\(\)\s*\?\s*1u\s*<<\s*(\d+)", source)
    assert len(mapping) == 12, mapping
    return {name: int(bit) for name, bit in mapping}

def serialize(mask):
    return tuple((mask >> bit) & 1 for bit in range(12))

def test_mapping():
    assert source_mapping() == EXPECTED

def test_onehot_identity():
    for bit in range(12):
        expected = tuple(int(i == bit) for i in range(12))
        assert serialize(1 << bit) == expected

def test_hold_no_false_transitions():
    for bit in range(12):
        frames = [serialize(1 << bit) for _ in range(600)]
        assert len(set(frames)) == 1
        assert sum(frames[0]) == 1
        assert serialize(0) == (0,) * 12

def test_combinations():
    for mask in range(1 << 12):
        decoded = sum(value << bit for bit, value in enumerate(serialize(mask)))
        assert decoded == mask

if __name__ == "__main__":
    test_mapping()
    test_onehot_identity()
    test_hold_no_false_transitions()
    test_combinations()
    print("PASS: 12-slot source mapping and ideal serialization model; NOT hardware proof")
