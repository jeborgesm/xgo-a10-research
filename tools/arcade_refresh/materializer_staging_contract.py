#!/usr/bin/env python3
"""Host reference for Arcade materializer -> transient family staging handoff.

A marker is authorized only after BOTH runtime ZIP and outer ZFB converge.
"""
from __future__ import annotations
from dataclasses import dataclass
from family_handoff import validate_name
from family_staging import marker_names

@dataclass(frozen=True)
class PhysicalResult:
    zfb_name:str
    zip_ok:bool
    zfb_ok:bool

def staged_identities(results:list[PhysicalResult])->list[str]:
    ready=[]
    for r in results:
        name=validate_name(r.zfb_name)
        if not r.zip_ok or not r.zfb_ok:
            raise RuntimeError(f"physical asset not converged: {name}")
        ready.append(name)
    return marker_names(ready)

def family_pass(existing_markers:list[str], results:list[PhysicalResult]):
    # Implementation contract is replace-set, never append stale markers.
    # existing_markers is intentionally ignored after validation of the new
    # physical results.
    return staged_identities(results)
