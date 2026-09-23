# Test129 rejection — protected-path isolation rule

Date: 2026-09-23
Status: **REJECTED BEFORE HARDWARE — never install**

The proposed Test129 diagnostic temporarily placed the GB materializer in the MD
helper slot to borrow the HW-proven Test97 lifecycle. The user correctly rejected
this because it mutates a protected, already-working subsystem and leaves the SD
layout semantically misleading if work is interrupted or context is lost.

## Permanent rule

For propagation work, diagnostic candidates MUST be subsystem-local.

- GB investigation may modify only GB-specific helper files plus the minimum
  command-3 dispatch bytes needed to reach them.
- GBC investigation may modify only GBC-specific helper files plus command 4.
- GBA investigation may modify only GBA-specific helper files plus command 5.
- Never replace FC/SFC/MD/CLASSIC helpers to test another system.
- Never borrow a protected system's pathname/slot by substituting foreign code.
- A candidate package must carry canonical protected helpers when the baseline
  package normally carries them; otherwise it must leave them untouched on card.
- Every builder must assert protected firmware bodies/routes remain identical to
  the selected baseline.

Test129 is archival evidence of a rejected design only. It must not be promoted,
tested, or used as an ancestor.

## Recovery baseline

Continue from exact Test123 protected firmware and the canonical HW-proven helper
set:
- FC: Test75 enrichment
- SFC: Test74 enrichment
- MD: Test106 hardened path
- CLASSIC: canonical Test72/Test123 helper
- GB: experimental only

The next diagnostic must reproduce the proven helper invocation lifecycle in a
GB-owned code/helper path rather than modifying MD.
