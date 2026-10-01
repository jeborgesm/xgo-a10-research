#!/usr/bin/env python3
"""Reference contract for transient Arcade family staging directories."""
from __future__ import annotations
from pathlib import PurePosixPath
from family_handoff import validate_name

SET_NAME=".refresh-set"

def marker_path(family_root: str, zfb_name: str) -> str:
    name=validate_name(zfb_name)
    return str(PurePosixPath(family_root)/SET_NAME/name)

def marker_names(processed_zfb_names):
    # Directory enumeration provides set semantics. Preserve first occurrence
    # here so host tests remain deterministic.
    out=[]; seen=set()
    for raw in processed_zfb_names:
        name=validate_name(raw)
        if name not in seen:
            seen.add(name); out.append(name)
    return out
