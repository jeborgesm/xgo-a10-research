#!/usr/bin/env python3
"""Host reference for the transient Arcade family handoff.

This is the executable specification for the on-device materializer/catalog
handoff. It intentionally contains no persistent classification state.
"""
from __future__ import annotations

MAX_NAME = 127
SUFFIX = ".zfb"

def validate_zfb_name(name: str) -> str:
    if not name or len(name.encode("ascii")) > MAX_NAME:
        raise ValueError("invalid name length")
    try:
        raw=name.encode("ascii")
    except UnicodeEncodeError as e:
        raise ValueError("manifest identity must be ASCII") from e
    if b"\x00" in raw or "\n" in name or "\r" in name:
        raise ValueError("control character in name")
    if "/" in name or "\\" in name or name in (".",".."):
        raise ValueError("not a basename")
    if not name.lower().endswith(SUFFIX):
        raise ValueError("not a .zfb identity")
    if len(name) <= len(SUFFIX):
        raise ValueError("empty stem")
    return name

def encode_manifest(names: list[str]) -> bytes:
    seen=set(); out=[]
    for n in names:
        n=validate_zfb_name(n)
        # Exact slot0 identity is case-sensitive. Duplicate exact identities
        # inside one invocation are collapsed without reordering.
        if n not in seen:
            seen.add(n); out.append(n)
    return ("".join(n+"\n" for n in out)).encode("ascii")

def decode_manifest(data: bytes) -> list[str]:
    if b"\x00" in data:
        raise ValueError("NUL in manifest")
    try:
        text=data.decode("ascii")
    except UnicodeDecodeError as e:
        raise ValueError("non-ASCII manifest") from e
    if text and not text.endswith("\n"):
        raise ValueError("unterminated final line")
    return [validate_zfb_name(x) for x in text.splitlines()]

def merge_slot0(existing: list[str], manifest: bytes) -> list[str]:
    """Reference stable-append identity result; slot1/2 use basename fallback."""
    out=list(existing)
    have=set(existing)
    for n in decode_manifest(manifest):
        if n not in have:
            out.append(n); have.add(n)
    return out
