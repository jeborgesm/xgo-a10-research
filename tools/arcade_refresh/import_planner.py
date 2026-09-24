#!/usr/bin/env python3
"""Pure planning rules for XGO four-family Arcade Refresh.

This module performs no I/O. It makes collision/idempotence decisions explicit
so host tests and the eventual MIPS worker can share one documented contract.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto

class Decision(Enum):
    IMPORT = auto()
    NO_CHANGE = auto()
    FAIL_ZIP_COLLISION = auto()
    FAIL_ZFB_COLLISION = auto()
    FAIL_CROSS_FAMILY = auto()

@dataclass(frozen=True)
class Existing:
    runtime_zip_exists: bool
    runtime_zip_identical: bool
    zfb_exists: bool
    zfb_driver: str | None
    target_family_has_zfb: bool
    other_family_has_zfb: bool

@dataclass(frozen=True)
class Plan:
    decision: Decision
    copy_zip: bool = False
    create_zfb: bool = False
    append_catalog: bool = False
    reason: str = ""


def plan(driver_zip: str, zfb_name: str, e: Existing) -> Plan:
    if e.runtime_zip_exists and not e.runtime_zip_identical:
        return Plan(Decision.FAIL_ZIP_COLLISION, reason="same driver ZIP basename has different bytes")

    if e.zfb_exists and e.zfb_driver != driver_zip:
        return Plan(Decision.FAIL_ZFB_COLLISION, reason="outer ZFB exists but targets a different driver")

    if e.other_family_has_zfb and not e.target_family_has_zfb:
        return Plan(Decision.FAIL_CROSS_FAMILY, reason="same outer ZFB identity is cataloged by another Arcade family")

    # Catalog membership is the convergence key. Existing compatible physical
    # assets are reusable; missing assets are repaired before catalog append.
    if e.target_family_has_zfb:
        if e.runtime_zip_exists and e.zfb_exists:
            return Plan(Decision.NO_CHANGE, reason="family catalog and physical assets already converge")
        # A catalog entry whose launch assets are missing is not a normal
        # append case. Fail closed; reconciliation/repair is separate.
        return Plan(Decision.FAIL_ZFB_COLLISION, reason="catalog entry exists but required physical asset is missing")

    return Plan(
        Decision.IMPORT,
        copy_zip=not e.runtime_zip_exists,
        create_zfb=not e.zfb_exists,
        append_catalog=True,
        reason="new family entry; reuse any byte-compatible physical assets",
    )
