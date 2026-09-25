#!/usr/bin/env python3
"""Reference state machine for Arcade manifest discovery -> proven catalog merge.

This captures the control-flow replacement required around the final GBA
catalog helper. It deliberately models only discovery and exact slot0 identity;
triplet serialization remains the inherited catalog engine.
"""
from __future__ import annotations
from dataclasses import dataclass
from family_handoff import decode_manifest

@dataclass(frozen=True)
class Candidate:
    filename: str
    stem: str

def candidates(manifest: bytes, physical_zfb: set[str]) -> list[Candidate]:
    out=[]
    for name in decode_manifest(manifest):
        # The on-device implementation must verify the real wrapper before
        # presenting an identity to the inherited catalog engine.
        if name not in physical_zfb:
            raise FileNotFoundError(name)
        out.append(Candidate(name, name[:-4]))
    return out

def missing_candidates(manifest: bytes, physical_zfb: set[str],
                       existing_slot0: list[str]) -> list[Candidate]:
    have=set(existing_slot0)
    return [c for c in candidates(manifest, physical_zfb) if c.filename not in have]
