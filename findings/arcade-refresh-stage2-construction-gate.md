# Arcade Refresh - Stage2 construction gate

Date: 2026-09-24
Branch: research-arcade-refresh-four-family

A guarded deterministic builder now exists at:
tools/arcade_refresh/build_catalog_stage2.py

It accepts only the exact HW-proven Test106 Stage2:
- size 7000
- SHA 45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c

Current emitted files are deliberately named *.partial.

The builder currently performs only modifications whose exact byte locations
have been directly audited:
- .zmd -> .zfb predicate:
  +0x0444 m->f
  +0x0470 d->b
- removes the exact MD count-cache invalidation sequence at +0x1A44..+0x1A4F
  by replacing all three instructions with NOPs.

It validates the expected original bytes before every patch and preserves the
7000-byte geometry.

Family-specific path substitutions are represented as descriptor data but are
NOT yet emitted. Exact Test106 literal offsets and capacities must be audited
before those writes are enabled. This prevents accidental broad string
replacement or overlap.

No *.partial output is a firmware candidate.
